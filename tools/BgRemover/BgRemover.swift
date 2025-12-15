#!/usr/bin/env swift
//
// BgRemover - macOS背景透過CLIツール
// Vision frameworkを使用した高精度な背景除去
//
// 使用方法:
//   ./BgRemover <入力画像> <出力画像>
//   ./BgRemover input.png output.png
//

import Foundation
import AppKit
import Vision
import CoreImage
import UniformTypeIdentifiers

// MARK: - エラー定義
enum BgRemoverError: Error, LocalizedError {
    case invalidArguments
    case fileNotFound(String)
    case imageLoadFailed(String)
    case processingFailed(String)
    case saveFailed(String)

    var errorDescription: String? {
        switch self {
        case .invalidArguments:
            return "使用方法: BgRemover <入力画像> <出力画像>"
        case .fileNotFound(let path):
            return "ファイルが見つかりません: \(path)"
        case .imageLoadFailed(let path):
            return "画像の読み込みに失敗しました: \(path)"
        case .processingFailed(let reason):
            return "処理に失敗しました: \(reason)"
        case .saveFailed(let path):
            return "保存に失敗しました: \(path)"
        }
    }
}

// MARK: - 背景除去処理
class BackgroundRemover {

    /// 背景を除去して透過PNG画像を生成
    func removeBackground(inputPath: String, outputPath: String) throws {
        // 入力ファイルの存在確認
        guard FileManager.default.fileExists(atPath: inputPath) else {
            throw BgRemoverError.fileNotFound(inputPath)
        }

        // 画像を読み込み
        guard let inputImage = NSImage(contentsOfFile: inputPath),
              let cgImage = inputImage.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
            throw BgRemoverError.imageLoadFailed(inputPath)
        }

        print("処理中: \(inputPath)")
        print("画像サイズ: \(cgImage.width) x \(cgImage.height)")

        // Vision リクエストを作成（人物セグメンテーション）
        let request = VNGeneratePersonSegmentationRequest()
        request.qualityLevel = .accurate  // 高精度モード
        request.outputPixelFormat = kCVPixelFormatType_OneComponent8

        // リクエストハンドラを作成して実行
        let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])

        do {
            try handler.perform([request])
        } catch {
            throw BgRemoverError.processingFailed(error.localizedDescription)
        }

        // 結果を取得
        guard let result = request.results?.first else {
            throw BgRemoverError.processingFailed("セグメンテーション結果を取得できませんでした")
        }
        let maskBuffer = result.pixelBuffer

        // マスクを使って背景を透過
        guard let outputImage = applyMask(to: cgImage, mask: maskBuffer) else {
            throw BgRemoverError.processingFailed("マスク適用に失敗しました")
        }

        // PNGとして保存
        try saveAsPNG(image: outputImage, to: outputPath)

        print("完了: \(outputPath)")
    }

    /// マスクを適用して背景を透過
    private func applyMask(to image: CGImage, mask: CVPixelBuffer) -> CGImage? {
        let ciImage = CIImage(cgImage: image)
        let maskImage = CIImage(cvPixelBuffer: mask)

        // マスクを元画像のサイズにリサイズ
        let scaleX = ciImage.extent.width / maskImage.extent.width
        let scaleY = ciImage.extent.height / maskImage.extent.height
        let scaledMask = maskImage.transformed(by: CGAffineTransform(scaleX: scaleX, y: scaleY))

        // ブレンドフィルターを使用してマスクを適用
        guard let blendFilter = CIFilter(name: "CIBlendWithMask") else {
            return nil
        }

        // 透明な背景画像を作成
        let clearColor = CIColor(red: 0, green: 0, blue: 0, alpha: 0)
        let clearImage = CIImage(color: clearColor).cropped(to: ciImage.extent)

        blendFilter.setValue(ciImage, forKey: kCIInputImageKey)
        blendFilter.setValue(clearImage, forKey: kCIInputBackgroundImageKey)
        blendFilter.setValue(scaledMask, forKey: kCIInputMaskImageKey)

        guard let outputCIImage = blendFilter.outputImage else {
            return nil
        }

        // CGImageに変換
        let context = CIContext()
        return context.createCGImage(outputCIImage, from: outputCIImage.extent)
    }

    /// PNGとして保存
    private func saveAsPNG(image: CGImage, to path: String) throws {
        let url = URL(fileURLWithPath: path)

        guard let destination = CGImageDestinationCreateWithURL(url as CFURL, UTType.png.identifier as CFString, 1, nil) else {
            throw BgRemoverError.saveFailed(path)
        }

        CGImageDestinationAddImage(destination, image, nil)

        if !CGImageDestinationFinalize(destination) {
            throw BgRemoverError.saveFailed(path)
        }
    }
}

// MARK: - メイン処理
func main() {
    let args = CommandLine.arguments

    // 引数チェック
    guard args.count == 3 else {
        print("BgRemover - macOS背景透過ツール (Vision framework使用)")
        print("")
        print("使用方法:")
        print("  \(args[0]) <入力画像> <出力画像>")
        print("")
        print("例:")
        print("  \(args[0]) photo.jpg output.png")
        print("  \(args[0]) ~/Pictures/image.png ~/Desktop/transparent.png")
        print("")
        print("対応形式: PNG, JPEG, GIF, BMP, TIFF")
        print("出力: PNG (透過対応)")
        exit(1)
    }

    let inputPath = (args[1] as NSString).expandingTildeInPath
    let outputPath = (args[2] as NSString).expandingTildeInPath

    let remover = BackgroundRemover()

    do {
        try remover.removeBackground(inputPath: inputPath, outputPath: outputPath)
        exit(0)
    } catch {
        print("エラー: \(error.localizedDescription)")
        exit(1)
    }
}

main()

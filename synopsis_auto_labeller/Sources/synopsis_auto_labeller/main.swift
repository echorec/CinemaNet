import Foundation
import SPMUtility

import Vision
import CoreML

let arguments = Array(ProcessInfo.processInfo.arguments.dropFirst())
let parser = ArgumentParser(usage: "<options>", overview: "Use a folder of ML model classifiers to label a local unlabeled data set'")

let optionModeldir: OptionArgument<String> = parser.add(option: "--modeldir", shortName: "-m", kind: String.self, usage: "folder containing core ml models to use as labelers. Each image to label will be run through each model")
let optionImagedir: OptionArgument<String> = parser.add(option: "--imagedir", shortName: "-i", kind: String.self, usage: "folder containing unlabeled images to be labeled")
let optionOutput: OptionArgument<String> = parser.add(option: "--output", shortName: "-o", kind: String.self, usage: "destination for labeled file containing multi labels")
let optionPrefix: OptionArgument<String> = parser.add(option: "--prefix", shortName: "-pre", kind: String.self, usage: "image url prefix, useful for adding a cloud storage provider URLs to the CSV path")
let optionLimit: OptionArgument<Int> = parser.add(option: "--limit", shortName: "-l", kind: Int.self, usage: "limit the number of images we label - useful for testing")
let optionRandom: OptionArgument<Bool> = parser.add(option: "--random", shortName: "-r", kind: Bool.self, usage: "randomize the order of images before we label them - useful for testing")
let optionConfidence: OptionArgument<Int> = parser.add(option: "--confidence", shortName: "-c", kind: Int.self, usage: "The confidence score we need to meet or exceed to apply a class label to an image")

let fileManager = FileManager.default
let workingURL = URL.init(fileURLWithPath: fileManager.currentDirectoryPath)

var modelsURL = workingURL.appendingPathComponent("Models/Classifiers/Cleaned", isDirectory: true)
var imagesURL = workingURL.appendingPathComponent("images", isDirectory: true)
var labelsURL = workingURL.appendingPathComponent("labels.csv", isDirectory: true)
var labelsText = ""
var prefix:String? = nil
var limit = Int.max
var random = false
var confidence:Float = 0.75

var models:[VNCoreMLModel] = []
var visionSequenceRequestHandler = VNSequenceRequestHandler.init()

func processArguments(arguments: ArgumentParser.Result)
{
    // There surly must be a cleaner way to one line this
    modelsURL = arguments.get(optionModeldir) == nil ? modelsURL : URL.init(fileURLWithPath: arguments.get(optionModeldir)! )
    imagesURL = arguments.get(optionImagedir) == nil ? imagesURL : URL.init(fileURLWithPath: arguments.get(optionImagedir)! )
    labelsURL = arguments.get(optionOutput) == nil ? labelsURL : URL.init(fileURLWithPath: arguments.get(optionOutput)! )
    confidence = arguments.get(optionConfidence) == nil ? confidence :  Float( arguments.get(optionConfidence)! ) / 100.0
    limit = arguments.get(optionLimit) == nil ? limit :  arguments.get(optionLimit)!
    random = arguments.get(optionRandom) == nil ? random :  arguments.get(optionRandom)!

    print("will load models from \(modelsURL.absoluteString)")
    print("will load images from \(imagesURL.absoluteString)")
    print("will save labels to \(labelsURL.absoluteString)")
    
    print("")
    print("Loading Models")
    print("")
    
    loadModels()
    
    print("")
    print("Running Inference")
    print("")
    
    runInferenceForImages()

}

func loadModels()
{
    if var possibleModelURLSToLoad = try? fileManager.contentsOfDirectory(at: modelsURL, includingPropertiesForKeys: [], options: .skipsHiddenFiles)
    {
        possibleModelURLSToLoad = possibleModelURLSToLoad.sorted(by: { (a, b) -> Bool in
            return a.absoluteString < b.absoluteString;
        })
        
        for url in possibleModelURLSToLoad
        {
            if url.pathExtension == "mlmodel"
            {
                do {
                    let compiledUrl = try MLModel.compileModel(at: url)
                    let model = try MLModel(contentsOf: compiledUrl)

                    let visionModel = try VNCoreMLModel(for: model)
                    print("Loaded model: \(url.lastPathComponent)")
                    models.append(visionModel)
                    
                }
                catch {
                    print(error.localizedDescription)
                    print("Unable to load model: \(url.lastPathComponent)")
                }
            }
        }
    }
    else
    {
        print("Unable to find model directory, bailing")
        exit(EXIT_FAILURE)
    }
}

func runInferenceForImages()
{
    var count:Int = 0

    if let possibleImageURLSToLoad = fileManager.enumerator(at: imagesURL, includingPropertiesForKeys: [], options: .skipsHiddenFiles)
    {
        for case let imageURL as Foundation.URL in possibleImageURLSToLoad
        {
            if count > limit
            {
                break
            }
            
            if !imageURL.hasDirectoryPath && imageURL.pathExtension == "jpg"
            {
                runInferenceForImageAt(imageURL: imageURL)
                count += 1
            }
        }
//        possibleImageURLSToLoad = possibleImageURLSToLoad.sorted(by: { (a, b) -> Bool in
//            return a.absoluteString < b.absoluteString;
//        })
//
//        for imageURL in possibleImageURLSToLoad
//        {
//            runInferenceForImageAt(imageURL: imageURL)
//        }
    }
    else
    {
        print("Unable to find image directory, bailing")
        exit(EXIT_FAILURE)
    }

    do {
        try labelsText.write(to:labelsURL, atomically: true, encoding: .utf8)
    } catch {
        print("Failed to create label file")
        print("\(error)")
    }
}

func runInferenceForImageAt(imageURL:Foundation.URL)
{
    print("Calulating labels for Image: \(imageURL.absoluteString)")

    // we need a dispatch group to know when all of our requests have finished
    let imageGroup = DispatchGroup()
    
    // the computed labels above our confidence score
    var results:[String] = []

    
    // Remove file name and get the containing folder name - should be our label
    var knownLabel = imageURL.deletingLastPathComponent().lastPathComponent

    
    //    imageGroup.notify(queue: DispatchQueue.main, work: DispatchWorkItem(block: {
    
        // This row is done, hit the main queue and write out our labels to our CSV for this imahe
//        writeCSVRow(imageURL: imageURL, labels: results)
    
//    }))
    
    var currentRequests:[VNCoreMLRequest] = []
    
    for model in models
    {
        imageGroup.enter()
        
        let completionHandler:VNRequestCompletionHandler = { request, error in
            
//            DispatchQueue.main.sync {
            
                guard let requestResult = request.results else {
                    
//                    imageGroup.leave()
                    
                    return
                }
                
//                print(requestResult)
            
                for case let observation as VNClassificationObservation in requestResult
                {
                    // TODO: use our confidence score
                    if observation.confidence >= confidence
                    {
                        if !observation.identifier.hasSuffix(".na")
                        {
                            results.append( observation.identifier )
                        }
                    }
                }
            
                imageGroup.leave()

//            }
        }

        let imageRequest = VNCoreMLRequest(model: model, completionHandler: completionHandler)
        
        currentRequests.append(imageRequest)
        
    }

    
    do {
        try visionSequenceRequestHandler.perform(currentRequests, onImageURL: imageURL)
    }
    catch
    {
        // unwind all enters since we failed
        print("Unable to run inference on  image \(imageURL.lastPathComponent)")

        for _ in models
        {
            imageGroup.leave()
        }
        
    }
    
    imageGroup.wait()
    
    writeCSVRow(imageURL: imageURL, labels: results)

}

func writeCSVRow(imageURL:Foundation.URL, labels:[String])
{
    labelsText.append(contentsOf: imageURL.absoluteString)
    labelsText.append(contentsOf: ", ")
    labelsText.append(contentsOf: labels.joined(separator: ", "))
    labelsText.append(contentsOf: "\n")
//    print("Labels for Image: \(imageURL.absoluteString) : \(labels)")
}


let parsedArguments = try parser.parse(arguments)
processArguments(arguments: parsedArguments)



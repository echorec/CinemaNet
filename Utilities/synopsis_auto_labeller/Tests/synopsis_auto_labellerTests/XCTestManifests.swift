import XCTest

#if !canImport(ObjectiveC)
public func allTests() -> [XCTestCaseEntry] {
    return [
        testCase(synopsis_auto_labellerTests.allTests),
    ]
}
#endif

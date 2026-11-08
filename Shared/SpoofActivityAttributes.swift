import Foundation
import ActivityKit

/// Общие данные Live Activity (Dynamic Island).
/// Файл компилируется и в приложении, и в виджете — поэтому лежит в Shared.
struct SpoofActivityAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var locationName: String
        var startedAt: Date
    }

    var appName: String
}

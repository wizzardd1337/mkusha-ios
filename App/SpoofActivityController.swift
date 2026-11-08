import Foundation
import ActivityKit

/// Запуск/обновление/остановка Live Activity.
@MainActor
final class SpoofActivityController {
    static let shared = SpoofActivityController()

    private var activity: Activity<SpoofActivityAttributes>?

    private init() {}

    func start(locationName: String, startedAt: Date) {
        guard ActivityAuthorizationInfo().areActivitiesEnabled else {
            print("[mkusha] Live Activities disabled in Settings")
            return
        }

        let state = SpoofActivityAttributes.ContentState(
            locationName: locationName,
            startedAt: startedAt
        )

        if let activity {
            Task {
                await activity.update(ActivityContent(state: state, staleDate: nil))
            }
            return
        }

        do {
            activity = try Activity.request(
                attributes: SpoofActivityAttributes(appName: "mkusha ios"),
                content: ActivityContent(state: state, staleDate: nil),
                pushType: nil
            )
            print("[mkusha] Live Activity started")
        } catch {
            print("[mkusha] Live Activity failed: \(error.localizedDescription)")
        }
    }

    func end() {
        guard let activity else { return }
        self.activity = nil
        Task {
            await activity.end(nil, dismissalPolicy: .immediate)
        }
    }
}

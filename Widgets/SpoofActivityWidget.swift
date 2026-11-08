import WidgetKit
import SwiftUI
import ActivityKit

private let spoofGreen = Color(red: 0.24, green: 0.86, blue: 0.44)
private let timerEnd = Date.distantFuture

@main
struct MkushaWidgets: WidgetBundle {
    var body: some Widget {
        SpoofLiveActivity()
    }
}

struct SpoofLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: SpoofActivityAttributes.self) { context in
            // Экран блокировки / шторка
            HStack(spacing: 14) {
                ZStack {
                    Circle().fill(spoofGreen.opacity(0.22)).frame(width: 44, height: 44)
                    Circle().fill(spoofGreen).frame(width: 16, height: 16)
                        .overlay(Circle().strokeBorder(.white.opacity(0.9), lineWidth: 2))
                }

                VStack(alignment: .leading, spacing: 3) {
                    Text("mkusha ios")
                        .font(.system(size: 12, weight: .semibold, design: .rounded))
                        .foregroundStyle(.white.opacity(0.55))
                    Text(context.state.locationName)
                        .font(.system(size: 16, weight: .semibold, design: .rounded))
                        .foregroundStyle(.white)
                        .lineLimit(1)
                }

                Spacer(minLength: 8)

                Text(timerInterval: context.state.startedAt...timerEnd, countsDown: false)
                    .monospacedDigit()
                    .font(.system(size: 22, weight: .semibold, design: .rounded))
                    .foregroundStyle(.white)
            }
            .padding(.horizontal, 18)
            .padding(.vertical, 14)
            .activityBackgroundTint(Color.black.opacity(0.92))
            .activitySystemActionForegroundColor(.white)

        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    HStack(spacing: 6) {
                        Circle().fill(spoofGreen).frame(width: 8, height: 8)
                        Text("mkusha ios")
                            .font(.system(size: 13, weight: .semibold, design: .rounded))
                    }
                    .padding(.leading, 8)
                }

                DynamicIslandExpandedRegion(.trailing) {
                    Text(timerInterval: context.state.startedAt...timerEnd, countsDown: false)
                        .monospacedDigit()
                        .font(.system(size: 15, weight: .semibold, design: .rounded))
                        .padding(.trailing, 8)
                }

                DynamicIslandExpandedRegion(.bottom) {
                    Text(context.state.locationName)
                        .font(.system(size: 12, weight: .medium, design: .rounded))
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                        .padding(.horizontal, 10)
                }
            } compactLeading: {
                Text("mkusha ios")
                    .font(.system(size: 9, weight: .semibold, design: .rounded))
                    .minimumScaleFactor(0.55)
                    .lineLimit(1)
            } compactTrailing: {
                Text(timerInterval: context.state.startedAt...timerEnd, countsDown: false)
                    .monospacedDigit()
                    .font(.system(size: 11, weight: .semibold, design: .rounded))
            } minimal: {
                Text(timerInterval: context.state.startedAt...timerEnd, countsDown: false)
                    .monospacedDigit()
                    .font(.system(size: 10, weight: .semibold, design: .rounded))
            }
            .keylineTint(spoofGreen)
        }
    }
}

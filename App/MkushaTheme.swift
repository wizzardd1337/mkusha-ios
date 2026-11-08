import SwiftUI

/// Чёрно-белая тема в стиле Apple Liquid Glass.
enum MkushaTheme {
    static let bg = Color.black
    static let ink = Color.white
    static let dim = Color.white.opacity(0.58)
    static let line = Color.white.opacity(0.16)
    /// Зелёная точка в стиле «Локатор».
    static let spoofGreen = Color(red: 0.24, green: 0.86, blue: 0.44)
}

struct GlassPanel: ViewModifier {
    var radius: CGFloat = 28

    func body(content: Content) -> some View {
        content
            .background(
                .ultraThinMaterial,
                in: RoundedRectangle(cornerRadius: radius, style: .continuous)
            )
            .overlay(
                RoundedRectangle(cornerRadius: radius, style: .continuous)
                    .strokeBorder(
                        LinearGradient(
                            colors: [.white.opacity(0.34), .white.opacity(0.05)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ),
                        lineWidth: 0.8
                    )
            )
            .shadow(color: .black.opacity(0.45), radius: 24, y: 12)
    }
}

extension View {
    func glassPanel(radius: CGFloat = 28) -> some View {
        modifier(GlassPanel(radius: radius))
    }
}

/// Основная кнопка: белая «стеклянная» или прозрачная.
struct MkushaButtonStyle: ButtonStyle {
    var prominent: Bool = true
    var tint: Color = .white

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 17, weight: .semibold, design: .rounded))
            .foregroundStyle(prominent ? Color.black : Color.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 17)
            .background {
                RoundedRectangle(cornerRadius: 22, style: .continuous)
                    .fill(prominent ? tint : Color.white.opacity(0.06))
            }
            .overlay(
                RoundedRectangle(cornerRadius: 22, style: .continuous)
                    .strokeBorder(.white.opacity(prominent ? 0.0 : 0.18), lineWidth: 0.8)
            )
            .scaleEffect(configuration.isPressed ? 0.97 : 1)
            .animation(.spring(response: 0.28, dampingFraction: 0.72), value: configuration.isPressed)
    }
}

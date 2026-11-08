import SwiftUI

/// Зелёная пульсирующая точка в стиле «Локатор».
struct PulseMarker: View {
    @State private var pulse = false
    private let green = MkushaTheme.spoofGreen

    var body: some View {
        ZStack {
            // расходящаяся волна
            Circle()
                .fill(green.opacity(0.35))
                .frame(width: 64, height: 64)
                .scaleEffect(pulse ? 1.45 : 0.45)
                .opacity(pulse ? 0 : 0.85)

            // мягкое свечение
            Circle()
                .fill(green.opacity(0.22))
                .frame(width: 46, height: 46)

            // ядро
            Circle()
                .fill(green)
                .frame(width: 20, height: 20)
                .overlay(
                    Circle().strokeBorder(.white.opacity(0.95), lineWidth: 2.5)
                )
                .shadow(color: green.opacity(0.9), radius: 12)
        }
        .frame(width: 72, height: 72)
        .onAppear {
            withAnimation(.easeOut(duration: 1.8).repeatForever(autoreverses: false)) {
                pulse = true
            }
        }
    }
}

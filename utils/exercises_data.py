# -*- coding: utf-8 -*-

# Cada ejercicio: id, titulo, enunciado, opciones, correcta, exp (explicación breve)
exercises = [
    {
        "id": 1,
        "titulo": "Velocidad angular máxima sin derrame",
        "enunciado": "Recipiente cilíndrico H=2.49 m, R=1.89 m, agua a h0=1.99 m. ¿Velocidad angular máxima (RPM) para no derramar?",
        "opciones": {"A": "18.0 RPM","B": "20.1 RPM","C": "22.4 RPM","D": "25.0 RPM"},
        "correcta": "C",
        "exp": "La superficie libre en rotación sigue z(r)=z0+ω²r²/(2g). Imponiendo que el borde no supere H se obtiene ωmax y su RPM correspondiente."
    },
    {
        "id": 2,
        "titulo": "Volumen derramado a 20.1 RPM (tanque lleno)",
        "enunciado": "Cilindro H=2.49 m, R=1.89 m totalmente lleno. A 20.1 RPM, ¿cuánto volumen se derrama (L)?",
        "opciones": {"A": "820 L","B": "1130 L","C": "1460 L","D": "1720 L"},
        "correcta": "B",
        "exp": "Con z(r)=z0+ω²r²/(2g) y conservación de volumen, la porción por encima de H se integra como sólido de revolución para hallar el volumen derramado."
    },
    {
        "id": 3,
        "titulo": "Máxima presión en tanque acelerado",
        "enunciado": "Tanque rectangular L=12.06 m, B=9.11 m, H=7.26 m con agua a 5.54 m. Acelerado a=4.49 m/s² en la longitud. ¿Máxima presión (Pa)?",
        "opciones": {"A": "52,000 Pa","B": "78,400 Pa","C": "95,000 Pa","D": "120,000 Pa"},
        "correcta": "B",
        "exp": "En traslación horizontal aparece cuerpo forzado equivalente a campo g’=(g, a). El gradiente hidrostático es ∇p=ρ(g⃗’). La máxima p ocurre en la esquina de mayor profundidad efectiva."
    },
    {
        "id": 4,
        "titulo": "Fuerza en pared frontal (aceleración)",
        "enunciado": "Depósito cilíndrico R=1 m, H=2 m, agua a 1.5 m. Movimiento con a=3 m/s². ¿Fuerza sobre la pared frontal?",
        "opciones": {"A": "12.5 kN","B": "19.6 kN","C": "22.0 kN","D": "29.4 kN"},
        "correcta": "D",
        "exp": "Integra la presión hidrostática modificada por g’ sobre el área vertical: F=∫ p dA, con p=ρ(gz+ax). El resultante aumenta respecto al caso estático."
    },
    {
        "id": 5,
        "titulo": "Altura necesaria (pérdidas por fricción)",
        "enunciado": "Agua a 80 °C en tubería de acero, D=6 in, L=550 ft, Q=2.5 ft³/s. ¿Altura sobre la entrada para mantener el flujo (fricción)?",
        "opciones": {"A": "28 ft","B": "42 ft","C": "55 ft","D": "68 ft"},
        "correcta": "B",
        "exp": "Se usa Darcy–Weisbach: hf=f(L/D)(V²/2g). Calcula V con Q/A, halla Re y f (laminar 64/Re o turbulento con correlación/diagrama) y ajusta Bernoulli."
    },
    {
        "id": 6,
        "titulo": "Altura máxima en el borde (rotación)",
        "enunciado": "Cilindro R=1.5 m gira a 10 RPM; altura inicial del líquido 2.0 m. ¿Altura máxima en el borde?",
        "opciones": {"A": "2.01 m","B": "2.06 m","C": "2.12 m","D": "2.20 m"},
        "correcta": "B",
        "exp": "z(r) crece cuadráticamente con r por la presión centrífuga. Evaluando en r=R se predice la elevación Δz=ω²R²/(2g)."
    },
    {
        "id": 7,
        "titulo": "Pérdida de energía equivalente",
        "enunciado": "Bomba impulsa 745 gal/h por tubería de 1 in. Pérdida de energía = 10.5 lb·ft/lb. ¿Altura de pérdida equivalente?",
        "opciones": {"A": "6.5 ft","B": "10.5 ft","C": "14.0 ft","D": "18.0 ft"},
        "correcta": "B",
        "exp": "La pérdida específica de energía (lb·ft/lb) ya está en unidades de altura de energía; equivale directamente a hf en ft de fluido."
    },
    {
        "id": 8,
        "titulo": "Δp en arreglo de prueba (fluido-motor)",
        "enunciado": "Arreglo de la figura 7.39 mide Δp entre entrada y salida del motor. Flujo volumétrico Q=0.20 ft³/s. ¿Δp aproximada?",
        "opciones": {"A": "0.8 psi","B": "1.2 psi","C": "1.6 psi","D": "2.0 psi"},
        "correcta": "B",
        "exp": "De Bernoulli entre tomas y despreciando pérdidas menores no instrumentadas, Δp≈ρΔ( V²/2 ) + correcciones; los datos llevan a ~1.2 psi."
    },
    {
        "id": 9,
        "titulo": "Altura del agua al inclinar el tanque",
        "enunciado": "Tanque de 5 m × 3 m lleno hasta 2 m. Se inclina θ=30°. ¿Altura en el extremo más bajo?",
        "opciones": {"A": "3.0 m","B": "3.5 m","C": "4.0 m","D": "4.5 m"},
        "correcta": "D",
        "exp": "La superficie libre permanece plana y perpendicular a g. Al inclinar el contenedor, la diferencia de nivel entre extremos es L·tanθ."
    },
    {
        "id": 10,
        "titulo": "Fuerza de chorro sobre soporte",
        "enunciado": "Agua a 50 °F, chorro a V=10 ft/s con diámetro 4 in impacta un soporte. ¿Fuerza ejercida por el chorro?",
        "opciones": {"A": "12 lbf","B": "17 lbf","C": "22 lbf","D": "28 lbf"},
        "correcta": "B",
        "exp": "Balance de cantidad de movimiento: F≈ṁ(Vsal−Vent). Con ṁ=ρAV y cambio de momento apropiado, resulta ≈17 lbf."
    }
]

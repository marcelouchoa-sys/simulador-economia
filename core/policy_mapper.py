def apply_policy_choice(choice, params):
    """
    Converte decisões qualitativas em mudanças quantitativas.
    """

    p = params.copy()

    if choice == "Expansão Fiscal":
        p["G"] += 100

    elif choice == "Contração Fiscal":
        p["G"] -= 100

    elif choice == "Expansão Monetária":
        p["M"] += 200

    elif choice == "Contração Monetária":
        p["M"] -= 200

    elif choice == "Aumento de Impostos":
        p["T"] += 50

    elif choice == "Corte de Impostos":
        p["T"] -= 50

    elif choice == "Alta Mobilidade de Capital":
        p["k"] += 0.2   # LM mais inclinada

    elif choice == "Baixa Mobilidade de Capital":
        p["k"] -= 0.2

    return p
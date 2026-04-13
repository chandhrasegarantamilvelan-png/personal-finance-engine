# EMI calculation function
def calculate_emi(P, r, n):
    # handle zero interest case
    if r == 0:
        return P / n
    
    return (P * r * (1 + r)**n) / ((1 + r)**n - 1)

def get_risk(emi_ratio):
    if emi_ratio <= 0.20:
        return "Safe"
    elif emi_ratio <= 0.30:
        return "Low Risk"
    elif emi_ratio <= 0.40:
        return "Moderate Risk"
    elif emi_ratio <= 0.50:
        return "High Risk"
    elif emi_ratio <= 0.75:
        return "Very High Risk"
    else:
        return "Unsustainable"
    

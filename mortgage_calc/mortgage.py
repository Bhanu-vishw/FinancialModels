"""
HW1 Solution
"""

def amortize(apr, years, balance, monthly_pmt=None):
    n = 12*years
    i = apr/12
    dict1 = {"period":[], "start_bal":[], "interest":[], "bal_after_int":[], "pmt":[], "bal_after_pmt":[], "principal_repaid":[]}
    if (monthly_pmt == None):
        v = 1/(1+i)
        ann = (1 - v**n)/i
        monthly_pmt = balance/ann
    for j in range (0, n):
        dict1["period"].append(j+1)
        if (j == 0):
            dict1["start_bal"].append(balance)
        else:
            dict1["start_bal"].append(dict1["bal_after_pmt"][j-1])
        dict1["interest"].append(dict1["start_bal"][j]*i)
        dict1["bal_after_int"].append(dict1["start_bal"][j] + dict1["interest"][j])
        if (j != n-1):
            k = min(monthly_pmt, dict1["bal_after_int"][j])
            dict1["pmt"].append(k)
        else:
            dict1["pmt"].append(dict1["bal_after_int"][j])
        dict1["bal_after_pmt"].append(dict1["bal_after_int"][j] - dict1["pmt"][j])
        dict1["principal_repaid"].append(dict1["start_bal"][j] - dict1["bal_after_pmt"][j])
        if (dict1["bal_after_pmt"][j] <= 1e-10):
            break
    return dict1 


def to_csv(fname, amortization_schedule, precision=2):
    list_out = []   
    l = len(amortization_schedule["period"])
    for i in range(0, l):
        list_out.append('\n')
        for val in amortization_schedule.values():
            list_out.append(round(val[i], precision))

    list_out_str = ['','period', 'start_bal', 'interest', 'bal_after_int', 'pmt', 'bal_after_pmt', 'principal_repaid']
    for i in range (0, len(list_out)):
        list_out_str.append(list_out[i])

    with open (f"{fname}.csv", 'w') as out_file:
        data =  map(str, list_out_str)
        dataset = ",".join(data)
        #print(dataset)
        out_file.writelines(f"{dataset}")   
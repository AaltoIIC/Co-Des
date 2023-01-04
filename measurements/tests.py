from find_optimal_design_threaded_measurements import test_func


FILENAME = "measurements1.csv"
NUMBER_OF_MEASUREMENTS = 100


DTID_OF_DDT = "https://dtid.org/2ef85647-aee2-40c5-bb5a-380c9563ed16"
LIST_OF_COMPONENT_CANDIDATES = ["https://dtid.org/e85c46f4-bdc2-4e0e-acd2-6b0ae582072d", "https://dtid.org/1febe1f0-16ff-4245-8fb2-759c93b01808", "https://dtid.org/efa0d72f-994d-4ad4-9f16-f1565371a18d", "https://dtid.org/6ae3e218-2152-4635-a61a-696c6e0584e6", "https://dtid.org/977bf820-fc6a-49c8-8002-388f7beb1148"]

def main():
    with open(FILENAME, "w") as f:
        f.write("ReadDDT,FindSuitableComponents,AnalyzingAssemblies,TotalTime\n")
    for _ in range(NUMBER_OF_MEASUREMENTS):
        test_func(DTID_OF_DDT, LIST_OF_COMPONENT_CANDIDATES, FILENAME)

if __name__ == "__main__":
    main()

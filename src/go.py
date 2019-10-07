import myfitnesspal

client = myfitnesspal.Client('seakeg')

day = client.get_date(2019, 10, 3)
day
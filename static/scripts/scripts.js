function populateYearSelect() {
    var selectElementFrom = document.getElementById("carYearSelectFrom");
    var selectElementTo = document.getElementById("carYearSelectTo");
    var currentYear = new Date().getFullYear();
    var startYear = 1980;

    for (var year = startYear; year <= currentYear; year++) {
        var optionFrom = document.createElement("option");
        optionFrom.value = year;
        optionFrom.text = year;
        selectElementFrom.appendChild(optionFrom);

        var optionTo = document.createElement("option");
        optionTo.value = year;
        optionTo.text = year;
        selectElementTo.appendChild(optionTo);
    }
}
populateYearSelect();
async function fetchCarMakes() {
    try {
        const response = await fetch('cars/makes');
        const jsonData = await response.json();

        return jsonData;
    } catch (error) {
        console.error('Error fetching car makes:', error);
    }
}

async function fetchCarModels(make) {
    try {
        const response = await fetch('cars/models/?make=' + make);
        const jsonData = await response.json();
        console.log(jsonData)

        return jsonData;
    } catch (error) {
        console.error('Error fetching car models:', error);
    }
}

async function populateSelect() {
    var selectElement = document.getElementById("carMakeSelect");
    const carMakes = await fetchCarMakes();

    if (carMakes) {
        carMakes.forEach(function (car) {
            var option = document.createElement("option");
            option.value = car.Marke;
            option.text = car.Marke;
            selectElement.appendChild(option);
        });
        fetchAndPopulateModels();
    }
}

async function fetchAndPopulateModels() {
    var selectedMake = document.getElementById("carMakeSelect").value;
    const carModels = await fetchCarModels(selectedMake);
    var selectElement = document.getElementById("carModelSelect");
    selectElement.innerHTML = "";

    var defaultOption = document.createElement("option");
    defaultOption.value = "all";
    defaultOption.text = "-";
    selectElement.appendChild(defaultOption);

    if (carModels) {
        carModels.forEach(function (model) {
            var option = document.createElement("option");
            option.value = model.Modelis;
            option.text = model.Modelis.toUpperCase();
            selectElement.appendChild(option);
        });
    }
}

function search() {
    var selectedMake = document.getElementById("carMakeSelect").value;
    var selectedModel = document.getElementById("carModelSelect").value;
    var selectedPriceFrom = document.getElementById("carPriceSelectFrom").value;
    var selectedPriceTo = document.getElementById("carPriceSelectTo").value;
    var selectedMileageFrom = document.getElementById("carMileageSelectFrom").value;
    var selectedMileageTo = document.getElementById("carMileageSelectTo").value;
    var selectedYearFrom = document.getElementById("carYearSelectFrom").value;
    var selectedYearTo = document.getElementById("carYearSelectTo").value;

    var url;
    if (selectedModel == "all")
    {
        url = "cars/?car_make=" + selectedMake;
    }
    else
    {
        url = "cars/?car_make=" + selectedMake + "&car_model=" + selectedModel;
    }
    url = addParameterIfExists(url, "price_from", selectedPriceFrom);
    url = addParameterIfExists(url, "price_to", selectedPriceTo);
    url = addParameterIfExists(url, "mileage_from", selectedMileageFrom);
    url = addParameterIfExists(url, "mileage_to", selectedMileageTo);
    url = addParameterIfExists(url, "year_from", selectedYearFrom);
    url = addParameterIfExists(url, "year_to", selectedYearTo);

    fetch(url)
        .then(response => {
            if (response.status === 200) {
                window.location.href = url;
            } else if (response.status === 403) {
                alert("You do not own this package!");
            } else {
                alert("Car not found!");
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

function addParameterIfExists(url, paramName, paramValue) {
    if (paramValue && paramValue !== "all") {
        url += "&" + paramName + "=" + paramValue;
    }
    return url;
}
populateSelect();


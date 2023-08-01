window.onload = function () {
    var selectElement = document.getElementById("mySelect");
    selectElement.addEventListener("change", function() {
    var selectedOption = selectElement.options[selectElement.selectedIndex];
    if(selectedOption.value == "Paid"){
        var new_element = document.createElement('div');
        new_element.classList.add("inputfield");
        new_element.setAttribute("id", "remv");
        var nested_label = document.createElement("label");
        var input_elem   = document.createElement("input");
        input_elem.setAttribute('name', 'price');
        nested_label.textContent = "Price";
        input_elem.setAttribute("type", "number");
        input_elem.classList.add("input");
        new_element.appendChild(nested_label);
        new_element.appendChild(input_elem);
        var referenceElement = document.querySelector(".custom_select_pricing");
        referenceElement.insertAdjacentElement('afterend', new_element);
    }
        else {
            try {
                var removeElement = document.getElementById("remv");
                removeElement.remove();
            }catch (error){
                console.log("The Element does not yet exist");
            }
        }
    } );
    var im_elem = document.getElementById("form_wrapper");
    im_elem.addEventListener("submit", function(e) {
        var fileInput = document.getElementById("myFile");
        var filePath = fileInput.value;
        var allowedExtensions = /(\.jpg|\.jpeg|\.png|\.gif)$/i;
      
        if (!allowedExtensions.exec(filePath)) {
          alert("Please select a file with a valid extension (jpg, jpeg, png, gif).");
          e.preventDefault();
          return false;
        }
      });
} 
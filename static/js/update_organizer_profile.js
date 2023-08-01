const checkYes  = document.getElementById("passYes");
const checkNo  = document.getElementById('passNo');
var selectElement = document.getElementById("changePass");
checkYes.addEventListener("click", revealPasswordFields);
console.log(checkYes.checked);
function revealPasswordFields(){
    if (checkYes.checked){
        alert("Yes");
        //Old Password
        var oldPasswordElement = document.createElement('div');
        oldPasswordElement.classList.add('remv');
        oldPasswordElement.classList.add('inputfield');
        let nestedOldPasswordLabel = document.createElement('label');
        nestedOldPasswordLabel.textContent = 'Old Password';
        let nestedOldPasswordInput = document.createElement('input');
        nestedOldPasswordInput.setAttribute('name', 'oldPass');
        nestedOldPasswordInput.setAttribute('type', 'password');
        nestedOldPasswordInput.classList.add('input');
        oldPasswordElement.setAttribute('id', 'oldpass');
        
        //New Password
        let newPasswordElement = document.createElement('div');
        newPasswordElement.classList.add('remv');
        newPasswordElement.classList.add('inputfield');
        let nestedNewPasswordLabel = document.createElement('label');
        nestedNewPasswordLabel.textContent = 'New Password';
        let nestedNewPasswordInput = document.createElement('input');
        nestedNewPasswordInput.setAttribute('type', 'password');
        nestedNewPasswordInput.classList.add('input');
        newPasswordElement.setAttribute('id', 'newpass');


        //Confirm Password
        let confirmNewPasswordElement = document.createElement('div');
        confirmNewPasswordElement.classList.add('remv');
        confirmNewPasswordElement.classList.add('inputfield');
        let confirmNestedNewPasswordLabel = document.createElement('label');
        confirmNestedNewPasswordLabel.textContent = 'Confirm Password';
        let confirmNestedNewPasswordInput = document.createElement('input');
        confirmNestedNewPasswordInput.setAttribute('type', 'password');
        confirmNestedNewPasswordInput.classList.add('input');
        confirmNewPasswordElement.setAttribute('id', 'Confirm');


        //oid
        oldPasswordElement.appendChild(nestedOldPasswordLabel);
        oldPasswordElement.appendChild(nestedOldPasswordInput);

        newPasswordElement.appendChild(nestedNewPasswordLabel);
        newPasswordElement.appendChild(nestedNewPasswordInput);

        confirmNewPasswordElement.appendChild(confirmNestedNewPasswordLabel);
        confirmNewPasswordElement.appendChild(confirmNestedNewPasswordInput);

        selectElement.insertAdjacentElement('afterend', oldPasswordElement);
        oldPasswordElement.insertAdjacentElement('afterend', newPasswordElement);
        newPasswordElement.insertAdjacentElement('afterend', confirmNewPasswordElement);

    }
}
checkNo.addEventListener('click', function() {
    if(checkNo.checked){
        alert("Yahoo");
        try {
            let removeElements = document.getElementsByClassName("remv");
            removeElements[0].remove();
            removeElements[2].remove();
            // removeElements[2].remove();
        } catch (error){
            console.log('The Element does not exist');
        }
    }

});
function change_icon(field_id,ico_id){
    var icon = document.getElementById(ico_id)
    var p_input = document.getElementById(field_id)
    icon.classList.toggle('fa-eye')
    if(p_input.getAttribute("type")=='password'){
        p_input.setAttribute('type','text')
    }
    else{
        p_input.setAttribute('type','password')
    }
}



function updateStatuses() {
    const statusEls = document.querySelectorAll(".status");
    const timeEls = document.querySelectorAll(".time-left");
    var sub_btn=document.querySelector(".submit-answer-btn")

    statusEls.forEach((statusEl, index) => {
        const timeEl = timeEls[index];
        const deadlineStr = statusEl.dataset.deadline; // get from data attribute
        const deadline = new Date(deadlineStr);
        const now = new Date();
        const diff = deadline - now;
        const date = new Date(diff)
        const role = document.getElementById("userrole").dataset.role

        if (diff <= 0) {
            if(role == "student"){
                statusEl.textContent = "Missed Deadline";
            }else{
                statusEl.textContent = "Closed";
            }
            timeEl.textContent = "0d 0h 0m 0s";
            timeEl.setAttribute('style','color:red');
            statusEl.setAttribute('style','color:red;');
            if(sub_btn){
                sub_btn.innerHTML="<span>You Missed the Deadline</span>";
                sub_btn.toggleAttribute('disabled',true);
                sub_btn.classList.remove('other-btn');
                sub_btn.classList.add('danger-btn');
                sub_btn.style.cursor='not-allowed'
            }
        } else {
            statusEl.textContent = "Active";
            statusEl.setAttribute('style','color:var(--ico-green);')
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = date.getUTCHours()
            const minutes = date.getUTCMinutes()
            const seconds = date.getUTCSeconds()
            timeEl.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
            timeEl.setAttribute('style','color: var(--purple);');
        }
    });
}

// Update every second
setInterval(updateStatuses, 1000);
updateStatuses();


// Message appear and disappear
function closemsg(divname){
    var div = document.querySelector(divname)
    div.classList.remove('appear-msg')
    div.classList.add('disappear-msg')
}

setTimeout(()=>{
    var div = document.querySelector('.message-div')
    if(div){div.classList.remove('appear-msg')
    div.classList.add('disappear-msg')}
},20000)





function loader(spinnerBg,form){
        const spinnerBgEl = document.querySelector(spinnerBg);
        const formEl = document.querySelector(form);
    if(formEl.checkValidity()){
        spinnerBgEl.style.display='flex'
    }
}





function showAttendance(col,data,at_btn,at_sv_btn,con_btn){
    const colEl = document.querySelector(col)
    const dataEls = document.querySelectorAll(data)
    const atBtnEl = document.querySelector(at_btn)
    const atSvBtnEl = document.querySelector(at_sv_btn)
    const conBtnEl = document.querySelector(con_btn)
   
    
    if(atBtnEl.textContent == "  Mark Attendece"){
        conBtnEl.classList.add("attendance-btn-group")
        atSvBtnEl.style.display='block'
        atBtnEl.innerHTML='<span><svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 18 18"><!-- Icon from Unicons Monochrome by Iconscout - https://github.com/Iconscout/unicons/blob/master/LICENSE --><path fill="currentColor" d="M7 18a1 1 0 0 1-.707-1.707l10-10a1 1 0 0 1 1.414 1.414l-10 10A1 1 0 0 1 7 18"/><path fill="currentColor" d="M17 18a1 1 0 0 1-.707-.293l-10-10a1 1 0 0 1 1.414-1.414l10 10A1 1 0 0 1 17 18"/></svg>&nbsp; Cancel</span>'
        if(colEl && dataEls){
        colEl.style.display='table-cell'
        dataEls.forEach(dataEl => {
            dataEl.style.display='block';
        })
    } 
    }
    else{
        conBtnEl.classList.remove("attendance-btn-group")
        atSvBtnEl.style.display='none'
        atBtnEl.innerHTML='<span><svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 18 18"><!-- Icon from Material Symbols by Google - https://github.com/google/material-design-icons/blob/master/LICENSE --><path fill="currentColor" d="m5.525 16.175l3.55-3.55q.3-.3.7-.288t.7.313q.275.3.275.7t-.275.7L6.25 18.3q-.3.3-.7.3t-.7-.3L2.7 16.15q-.275-.275-.275-.7t.275-.7t.7-.275t.7.275zm0-8l3.55-3.55q.3-.3.7-.288t.7.313q.275.3.275.7t-.275.7L6.25 10.3q-.3.3-.7.3t-.7-.3L2.7 8.15q-.275-.275-.275-.7t.275-.7t.7-.275t.7.275zM14 17q-.425 0-.712-.288T13 16t.288-.712T14 15h7q.425 0 .713.288T22 16t-.288.713T21 17zm0-8q-.425 0-.712-.288T13 8t.288-.712T14 7h7q.425 0 .713.288T22 8t-.288.713T21 9z"/></svg>&nbsp; Mark Attendece</span>'
        if(colEl && dataEls){
        colEl.style.display='none'
        dataEls.forEach(dataEl => {
            dataEl.style.display='none'
        })
    } 
    }
}



function submitAttForm(att_form){
    const attForm=document.querySelector(att_form)
    attForm.submit()
}




// dropdown
const dropbtn = document.querySelector('.dropbtn')
const dropdown_content = document.querySelector('.dropdown-content')
if (dropbtn){
    dropbtn.addEventListener("click",(e)=>{
        e.stopPropagation();
        dropdown_content.classList.add("active")
    })
    document.addEventListener("click",()=>{
        dropdown_content.classList.remove("active")
    })
}



// Image Preview
const noImage = document.querySelector('.no-image')
const imgInput = document.querySelector('.profile-image-file-input')
const profileText = document.querySelector('.profile-text')
const previousImage = document.querySelector('.previous-image')

var imagePlaceholder = NaN


document.addEventListener("DOMContentLoaded",()=>{
    if (noImage){
        profileText.style.display = 'block'
        noImage.style.display = 'none'
        imagePlaceholder = noImage

    }
    else if(previousImage){
        profileText.style.display = 'none'
        previousImage.style.display = 'block'
        imagePlaceholder = previousImage
    }
})


if(imagePlaceholder,imgInput,profileText){
    imgInput.addEventListener("change",()=>{
        if(imgInput.files && imgInput.files[0]){
            imgFile = imgInput.files[0]
            imagePlaceholder.src = URL.createObjectURL(imgFile)
            profileText.style.display = 'none'
            imagePlaceholder.classList.add('profile-image')
            imagePlaceholder.style.display = 'block'
        }
    })
}



console.log(USER_ID)
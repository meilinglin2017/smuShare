const inputs = document.querySelectorAll('.input');

function focusFunc(){
    let parent = this.parentNode.parentNode;
    parent.classList.add('focus');
};

function blurFunc(){
    let parent = this.parentNode.parentNode;
    if(this.value==''){
        parent.classList.remove('focus');
    }
};

inputs.forEach(input =>{
    input.addEventListener('focus', focusFunc);
    input.addEventListener('blur', blurFunc);
});

$('.search-button').click(function(){
    $(this).parent().toggleClass('open');
  });

const spans = document.querySelectorAll(".word span");

spans.forEach((span, idx) => {
    span.addEventListener("click", e => {
        e.target.classList.add("active");
    });
    span.addEventListener("animationend", e => {
        e.target.classList.remove("active");
    });

    // Initial animation
    setTimeout(() => {
        span.classList.add("active");
    }, 750 * (idx + 1));
});

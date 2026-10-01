
    function showAmount() {
        let category = document.getElementById("category").value;
        let amountBox = document.getElementById("amountBox");

        if (category == "생활") {
            amountBox.style.display = "block";
        } else {
            amountBox.style.display = "none";
        }
    }
async function getDef(word) {
  let init = {
      mode: 'cors',
      method: 'GET',
  }
                let url = "words/" + word.innerHTML;
                let resp = await fetch(url, init);
                console.log(resp);
                console.log(resp.body);
                myPromise = resp.text();
                let jp = myPromise.then(function (r) {
                  console.log(r);


                  document.getElementById("defHeader").innerHTML = "Definition of " + word.innerHTML + ":";
                  document.getElementById("definition").innerHTML = r;
                  document.getElementById("deff").style.display = "block";
                });
            }

function closeDef() {
  document.getElementById("deff").style.display = "none";
}

 $.ajax({
        url: 'https://smartpond-dashboard.firebaseio.com./smartpond-dashboard.json',
        type: "GET", /* POST or GET OK */
        data: JSON.stringify(param),

        success: function (data) {
            let obj = data;
            let arr = [];
            let arrChart_do = [];
            let arrChart_ph = [];
            let arrChart_tempr = [];
            
            for (var x in obj){
                arr.push(obj[x]);
            }
        
            var tempr = {temprval :arr[arr.length -1].val_tempr };
            var pH = {phval :arr[arr.length -1].val_ph };
            var dsox = {dsoxval :arr[arr.length -1].val_do };

            for (i=7; i>0; i--){
                arrChart_do.push(arr[arr.length-i].val_do);
                arrChart_ph.push(arr[arr.length-i].val_ph);
                arrChart_tempr.push(arr[arr.length-i].val_tempr);
              }
      
            firebasedata_do = arrChart_do;
            firebasedata_ph = arrChart_ph;
            firebasedata_tempr = arrChart_tempr;

        
            //Random Test
            /* var ii = Math.floor(Math.random()*8);
            var tempr = {temprval :arr[arr.length -ii].val_tempr};
            var pH = {phval :arr[arr.length -ii].val_ph};
            var dsox = {dsoxval :arr[arr.length -ii].val_do}; */
            //End of Random Test

            //console.log([tempr, pH, dsox]);
            //console.log(arr[arr.length -ii].val_tempr);
            $("#val_do").text(dsox.dsoxval)
            $("#val_ph").text(pH.phval)
            $("#val_tempr").text(tempr.temprval)
            progressNumber = dsox.dsoxval;
        },
        error: function(error) {
            console.log('Error: ' + error);
        }
        
    });
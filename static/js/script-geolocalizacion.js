
        //function enviarUbicacion(){
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(mostrarUbicacion);
            } else {
                alert("¡Error! Este navegador no soporta la Geolocalización.");
            }

            function mostrarUbicacion(position) {
                tecnico = document.getElementById("tecnico").value;
                var latitud = position.coords.latitude;
                var longitud = position.coords.longitude;
                
                //var div = document.getElementById("ubicacion");
                //div.innerHTML = "Latitud: " + latitud + "<br>Longitud: " + longitud ;
                window.location = '/add_localizacion?parametros=' + tecnico + ',' + latitud + ',' + longitud
            }	
        //}
    
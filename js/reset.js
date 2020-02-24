function get_result(){
	var pra = document.getElementById("record");
	var meg = pra.text;
	var s = ""
	var index = 0;
	s = index.toString();
	var tmp = "";
	for(var i = 0; i < 30; i++){
		index++;
		s = index.toString();
		sp = document.getElementById(s);
		tmp = meg.slice(i,i+1);
		sp.innerHTML = tmp;
	}
}


function reset() {  
	var password = prompt("please provide admin password", "");  
	var clearid = document.getElementById("clear");
	if(password != "12345"){  
		alert("you do not have enough priority!"); 
	}
	else{
		alert("Reset Successfully");
		clearid.action = "/clear";
	}
	
}

function check_priority() {
	var butt = document.getElementById("reg");
	butt.disabled = false;
	
	var formid = document.getElementById("form");
	
	var myselect = document.getElementById("type");
	var index = myselect.selectedIndex;
	if(myselect.options[index].text == "Stuff"){
		var password = prompt("please provide admin password", "");  
		if (password != "12345"){  
			 butt.disabled = true;
		}
		else{
			formid.action = "/registerS";
		}
	}
	if(myselect.options[index].text == "General User"){
		formid.action = "/registerU";
	}
	if(myselect.options[index].text == "Researcher"){
		formid.action = "/registerR";
	}
	
}
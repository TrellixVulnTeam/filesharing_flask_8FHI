
function ajax_request(request_method,parameters,url,callback){
	this.Request = new XMLHttpRequest();
	this.Request.open(request_method, url);
	if (request_method == 'POST'){
		Request.setRequestHeader(
			'Content-Type', 
			'application/x-www-form-urlencoded'
		);
	}
	this.Request.send(parameters);
	this.Request.onreadystatechange  = function () {
		if (Request.readyState>3 && Request.status==200){
			callback(Request.responseText,Request);
		}
	}
}

function mijncallback(result, Request){
	console.log(result);
	console.log(Request);
}

r = new ajax_request('GET',{test:'watisditdan'},'http://127.0.0.1',mijncallback);


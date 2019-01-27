window.onload = function() {
	function add_task(id,trigger)
	{
		if(trigger=='cron'){
			var trigger = '每天'
			}
		else{
			var trigger = '单次'
			}

		if(id.split('-')[1]=='true'){
			var state = '通电'
			}
		else{
			var state = '断电'
			}
		var time = id.split('-')[0]

		var $tr = "<tr><td>定时任务:"+ trigger + time + state+ "</td><td><a href='javascript:;'class='del' name='" + id + "'>删除任务</a></td></tr>>"
			$("#task").append($tr)
	}

	$.get("http://39.108.210.212/task/", function (result) {
		for(var o in result){
			add_task(o,result[o])
  		}
	});

	if(state) {
		document.getElementById('timeTips').innerHTML = '插座已通电'
	} else {
		document.getElementById('timeTips').innerHTML = '插座已断电'
	}

	$("input#on").on('click', function() {
		state = true
		$.post("http://39.108.210.212/post/", {state: "true"},
			function(result) {
				if(result['msg'] == 'ok') {
					document.getElementById('timeTips').innerHTML = '插座已通电'
				}
			})
	});

	$("input#off").on('click', function() {
		state = false
		$.post("http://39.108.210.212/post/", {state: "false"},
			function(result) {
				if(result['msg'] == 'ok') {
					document.getElementById('timeTips').innerHTML = '插座已断电'
				}
			})
	});

	$("input#order_on").on('click', function() {
		var trigger = document.getElementById("trigger1").value;
		var time = document.getElementById("timer1").value;
		var name = time + '-true'
		if(time) {
			$.post("http://39.108.210.212/post/", {
				trigger: trigger,
				state: "true",
				date: time
			}, function(result) {
				if(result['msg'] == 'ok') {
					add_task(name,trigger)
				}
			})
		}
		else {
			alert('请输入正确的时间')
		}

	});

	$("input#order_off").on('click', function() {
		var trigger = document.getElementById("trigger2").value;
		var time = document.getElementById("timer2").value;
		var name = time + '-false'

		if(time) {
			$.post("http://39.108.210.212/post/", {
				trigger: trigger,
				state: "false",
				date: time
			}, function(result) {
				if(result['msg'] == 'ok') {
					add_task(name,trigger)
				}
			})
		} else {
			alert('请输入正确的时间')
		}
	});

	$('#task').on('click', '.del', function() {

		$.get("http://39.108.210.212/delete/", {
			id: this.name
		});
		$(this).parent().parent().remove()
	});
}
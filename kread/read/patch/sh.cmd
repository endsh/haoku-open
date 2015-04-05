sh.enableSharding('index')  +  sh.enableSharding('read')  +  sh.enableSharding('spider')  +  sh.enableSharding('sim') + sh.shardCollection('read.article',{_id:1}) + sh.shardCollection('spider.article',{_id:1}) + sh.shardCollection('spider.exc_article',{_id:1}) + sh.shardCollection('index.index',{word:1}) + sh.shardCollection('index.index_keys',{_id:1}) + sh.shardCollection('index.topic',{word:1}) + sh.shardCollection('index.topic_keys',{_id:1}) + sh.shardCollection('sim.sim',{_id:1}) + sh.shardCollection('sim.sim0',{_id:1}) + sh.shardCollection('sim.sim1',{_id:1}) + sh.shardCollection('sim.sim2',{_id:1}) + sh.shardCollection('sim.sim3',{_id:1})

sh.enableSharding('index')  +  sh.enableSharding('read')  +  sh.enableSharding('spider')  +  sh.enableSharding('sim') + sh.shardCollection('read.article',{_id:1}) + sh.shardCollection('spider.article',{_id:1}) + sh.shardCollection('spider.exc_article',{_id:1}) + sh.shardCollection('index.index',{word:1}) + sh.shardCollection('index.index_keys',{_id:1}) + sh.shardCollection('index.topic',{word:1}) + sh.shardCollection('index.topic_keys',{_id:1}) + sh.shardCollection('sim.sim',{_id:1}) + sh.shardCollection('sim.sim0',{_id:1}) + sh.shardCollection('sim.sim1',{_id:1}) + sh.shardCollection('sim.sim2',{_id:1}) + sh.shardCollection('sim.sim3',{_id:1})


var hosts = ["hkset0/coolnote.cn:30001,haocool.net:30001",
		"hkset1/coolnote.cn:30002,haocool.net:30002",
		"hkset2/chiki.org:30001,formatter.org:30001",
		"hkset3/51ku.net:30001,formatter.org:30002",
		"hkset4/51ku.net:30002,chiki.org:30002"];
var code = '0123456789abcdef';
var tables = ['read.article', 'spider.article', 'spider.exc_article'];
for (var i = 0; i < tables.length; i++) {
	var table = tables[i];
	for ( var x = 0; x < 256; x++ ) {
		var prefix = code[Math.floor(x / 16)] + code[x % 16];
		var old = prefix + 'a';
		var toset = hosts[Math.floor(x / 52)];
		db.runCommand( { split : table , middle : { _id : prefix } } );
		db.adminCommand({moveChunk: table, find:{_id:old}, to: toset})
	}
};


var start = -9223372036854775807;
var end = 9223372036854775807;
var off = end - start;
var hosts = ["hkset0/coolnote.cn:30001,haocool.net:30001",
		"hkset1/coolnote.cn:30002,haocool.net:30002",
		"hkset2/chiki.org:30001,formatter.org:30001",
		"hkset3/51ku.net:30001,formatter.org:30002",
		"hkset4/51ku.net:30002,chiki.org:30002"];
var tables = ['sim.sim', 'sim.sim0', 'sim.sim1', 'sim.sim2', 'sim.sim3'];
for (var i = 0; i < tables.length; i++) {
	var table = tables[i];
	for (var x = 0; x < 50; x += 1) {
		var prefix = start + off / 100 + off / 50 * x;
		var toset = hosts[Math.floor(x / 10)];
		db.runCommand({ split : table , middle : { _id : prefix } } );
		db.adminCommand({moveChunk: table, find:{_id:prefix + 1}, to: toset})
	}
}


var start = -9223372036854775807;
var end = 9223372036854775807;
var off = end - start;
var hosts = ["hkset0/coolnote.cn:30001,haocool.net:30001",
		"hkset1/coolnote.cn:30002,haocool.net:30002",
		"hkset2/chiki.org:30001,formatter.org:30001",
		"hkset3/51ku.net:30001,formatter.org:30002",
		"hkset4/51ku.net:30002,chiki.org:30002"];
var tables = ['index.index_keys', 'index.topic_keys'];
for (var i = 0; i < tables.length; i++) {
	var table = tables[i];
	for (var x = 0; x < 200; x += 1) {
		var prefix = start + off / 400 + off / 200 * x;
		var toset = hosts[Math.floor(x / 40)];
		db.runCommand({ split : table , middle : { _id : prefix } } );
		db.adminCommand({moveChunk: table, find:{_id:prefix + 1}, to: toset})
	}
}


var start = -9223372036854775807;
var end = 9223372036854775807;
var off = end - start;
var hosts = ["hkset0/coolnote.cn:30001,haocool.net:30001",
		"hkset1/coolnote.cn:30002,haocool.net:30002",
		"hkset2/chiki.org:30001,formatter.org:30001",
		"hkset3/51ku.net:30001,formatter.org:30002",
		"hkset4/51ku.net:30002,chiki.org:30002"];
var tables = ['index.index', 'index.topic'];
for (var i = 0; i < tables.length; i++) {
	var table = tables[i];
	for (var x = 0; x < 50; x += 1) {
		var prefix = start + off / 100 + off / 50 * x;
		var toset = hosts[Math.floor(x / 10)];
		db.runCommand({ split : table , middle : { word : prefix } } );
		db.adminCommand({moveChunk: table, find:{ word : prefix + 1}, to: toset})
	}
}


var hosts = ["hkset0/coolnote.cn:30001,haocool.net:30001",
		"hkset1/coolnote.cn:30002,haocool.net:30002",
		"hkset2/chiki.org:30001,formatter.org:30001",
		"hkset3/51ku.net:30001,formatter.org:30002",
		"hkset4/51ku.net:30002,chiki.org:30002"];
var code = '0123456789abcdef';
var tables = ['spider.image'];
for (var i = 0; i < tables.length; i++) {
	var table = tables[i];
	for ( var x = 0; x < 256; x++ ) {
		var prefix = code[Math.floor(x / 16)] + code[x % 16];
		var old = prefix + 'a';
		var toset = hosts[Math.floor(x / 52)];
		db.runCommand( { split : table , middle : { _id : prefix } } );
		db.adminCommand({moveChunk: table, find:{_id:old}, to: toset})
	}
};
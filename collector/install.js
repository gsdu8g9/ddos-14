var pg = require('pg');

var config = require('../config.json').database;
config.master = 'postgres';

//var config = {
//    user: 'postgres',
//    password: '123456',
//    database: 'postgres',
//    new_database: 'traffic',
//    host: 'localhost',
//    port: 5432
//};




var get_create_db = function () {
    return "CREATE DATABASE " + config.database +
        "  WITH OWNER = " + config.user +
        "       ENCODING = 'UTF8'\n" +
        "       TABLESPACE = pg_default\n" +
        "       CONNECTION LIMIT = -1;";
};

var get_create_table_flows = function () {
    return "CREATE TABLE IF NOT EXISTS flows (" +
        "   id   SERIAL NOT NULL, " +
        "   time TIMESTAMP NOT NULL, " +
        "   data TEXT[], " +
        "   atk_name VARCHAR(250)," + 
        "   atk_desc TEXT," + 
        "   PRIMARY KEY(id));";
};

var get_create_table_addresses = function () {
    return "CREATE TABLE IF NOT EXISTS addresses (" +
        "   id   SERIAL NOT NULL, " +
        "   time TIMESTAMP NOT NULL, " +
        "   address TEXT," + 
        "   PRIMARY KEY(id));";
};

var get_drop_db = function () {
    return "DROP DATABASE IF EXISTS " + config.database;
};


var createTable = function (c) {
    var client = new pg.Client(config);
    client.connect();
    var query = client.query(get_create_table_flows());
    query.on('end', function () {
        client.end();
        console.log("* Table created!");
        c();
    });
};

var create = function () {
    
    var _db = config.database;
    config.database = config.master;
    var client = new pg.Client(config);
    client.connect();
    config.database = _db;
    
    var query1 = client.query(get_drop_db());
    query1.on('end', function () {
        console.log("* DB deleted!");
        var query2 = client.query(get_create_db());
        query2.on('end', function () {
            client.end();
            console.log("* DB created!");
            createTable(function () {
                console.log("[v] All done!");
            }); 
        });
    });

};

create();
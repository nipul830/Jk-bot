package com.royalinstitute.mobile

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class RoyalApi(private val baseUrl:String, private val token:String){
    private suspend fun request(path:String,method:String="GET"):String?=withContext(Dispatchers.IO){
        try{
            val c=URL(baseUrl.trimEnd('/')+path).openConnection() as HttpURLConnection
            c.requestMethod=method;c.connectTimeout=8000;c.readTimeout=8000
            c.setRequestProperty("Authorization","Bearer $token");c.setRequestProperty("Accept","application/json")
            val stream=if(c.responseCode in 200..299)c.inputStream else c.errorStream
            stream?.bufferedReader()?.use{it.readText()}
        }catch(_:Exception){null}
    }
    suspend fun state():DashboardState?{
        val raw=request("/api/state")?:return null
        return try{val o=JSONObject(raw);val a=o.optJSONObject("account");DashboardState(o.optBoolean("mt5_connected"),o.optBoolean("engine_running"),a?.optDouble("balance")?:0.0,a?.optDouble("equity")?:0.0)}catch(_:Exception){null}
    }
    suspend fun start()=request("/api/start","POST")!=null
    suspend fun stop()=request("/api/stop","POST")!=null
}

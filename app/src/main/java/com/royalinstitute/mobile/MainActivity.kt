package com.royalinstitute.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch

private val Bg = Color(0xFF0B0D10)
private val Card = Color(0xFF141820)
private val Muted = Color(0xFF9AA4B2)
private val Accent = Color(0xFF7C5CFC)

data class SymbolRow(val symbol: String, val regime: String, val score: Double, val tier: String, val direction: Int)
data class DashboardState(val connected: Boolean=false, val running: Boolean=false, val balance: Double=0.0, val equity: Double=0.0, val symbols: List<SymbolRow> = emptyList())

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { RoyalInstituteApp() }
    }
}

@Composable
fun RoyalInstituteApp() {
    var state by remember { mutableStateOf(DashboardState()) }
    var serverUrl by remember { mutableStateOf("https://YOUR-SECURE-BRIDGE") }
    var token by remember { mutableStateOf("") }
    var message by remember { mutableStateOf("Not connected") }
    val scope = rememberCoroutineScope()

    MaterialTheme(colorScheme = darkColorScheme()) {
        Surface(Modifier.fillMaxSize(), color = Bg) {
            LazyColumn(Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                item {
                    Text("RoyalInstitute", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
                    Text("MT5 Mobile Control", color = Muted)
                }
                item {
                    OutlinedTextField(serverUrl, { serverUrl = it }, label={Text("Secure bridge URL")}, modifier=Modifier.fillMaxWidth(), singleLine=true)
                }
                item {
                    OutlinedTextField(token, { token = it }, label={Text("Session token")}, modifier=Modifier.fillMaxWidth(), singleLine=true)
                }
                item {
                    Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
                        Button(onClick={ scope.launch { val r=RoyalApi(serverUrl, token).state(); if(r!=null){state=r;message="Connected"}else message="Connection failed"} }) { Text("Connect") }
                        OutlinedButton(onClick={ scope.launch { val ok=RoyalApi(serverUrl, token).start(); message=if(ok)"Engine started" else "Start failed"; if(ok)state=state.copy(running=true) } }) { Text("Start") }
                        OutlinedButton(onClick={ scope.launch { val ok=RoyalApi(serverUrl, token).stop(); message=if(ok)"Engine stopped" else "Stop failed"; if(ok)state=state.copy(running=false) } }) { Text("Stop") }
                    }
                }
                item {
                    CardBox {
                        Text(if(state.running) "● ENGINE RUNNING" else "● ENGINE STOPPED", color=if(state.running) Color(0xFF52D273) else Color(0xFFFF6672), fontWeight=FontWeight.Bold)
                        Spacer(Modifier.height(8.dp))
                        Text("MT5: "+if(state.connected)"Connected" else "Disconnected", color=Muted)
                        Text(message, color=Muted)
                    }
                }
                item {
                    Row(horizontalArrangement=Arrangement.spacedBy(10.dp)) {
                        MetricCard("Balance", "%.2f".format(state.balance), Modifier.weight(1f))
                        MetricCard("Equity", "%.2f".format(state.equity), Modifier.weight(1f))
                    }
                }
                item { Text("Signals", style=MaterialTheme.typography.titleLarge, fontWeight=FontWeight.SemiBold) }
                items(state.symbols) { row ->
                    CardBox {
                        Row(Modifier.fillMaxWidth(), verticalAlignment=Alignment.CenterVertically) {
                            Column(Modifier.weight(1f)) { Text(row.symbol, fontWeight=FontWeight.Bold); Text(row.regime, color=Muted) }
                            Column(horizontalAlignment=Alignment.End) { Text("${row.score.toInt()}/100"); Text(row.tier, color=Accent, fontWeight=FontWeight.Bold) }
                        }
                    }
                }
            }
        }
    }
}

@Composable private fun CardBox(content: @Composable ColumnScope.()->Unit) = Column(Modifier.fillMaxWidth().background(Card, RoundedCornerShape(16.dp)).padding(16.dp), content=content)
@Composable private fun MetricCard(title:String,value:String,modifier:Modifier){ Column(modifier.background(Card,RoundedCornerShape(16.dp)).padding(16.dp)){Text(title,color=Muted);Spacer(Modifier.height(4.dp));Text(value,style=MaterialTheme.typography.titleLarge,fontWeight=FontWeight.Bold)} }

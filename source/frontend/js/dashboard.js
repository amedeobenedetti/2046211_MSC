const API = "http://localhost:8000"

async function loadSensors() {

    const res = await fetch(API + "/state")
    const data = await res.json()

    const container = document.getElementById("sensors")
    container.innerHTML = ""

    Object.values(data).forEach(sensor => {

        sensor.measurements.forEach(m => {

            const div = document.createElement("div")
            div.className = "sensor-card"

            div.innerHTML =
                "<b>" + sensor.source_name + "</b><br>" +
                m.metric + ": " +
                m.value + " " +
                m.unit

            container.appendChild(div)
        })

    })
}

setInterval(loadSensors, 5000)
loadSensors()
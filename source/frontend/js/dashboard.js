const API_URL = "http://localhost:8000/state"

async function loadSensors() {

    try {

        const res = await fetch(API_URL)
        const data = await res.json()

        const grid = document.getElementById("sensorGrid")
        grid.innerHTML = ""

        Object.values(data).forEach(sensor => {

            sensor.measurements.forEach(measure => {

                const card = document.createElement("div")
                card.className = "sensor-card"

                const statusClass = sensor.status === "ok"
                    ? "status-ok"
                    : "status-warning"

                card.innerHTML = `
                    <div class="sensor-title">
                        ${sensor.source_name}
                    </div>

                    <div class="sensor-value">
                        ${measure.value}
                    </div>

                    <div class="sensor-unit">
                        ${measure.metric} (${measure.unit})
                    </div>

                    <div class="${statusClass}">
                        status: ${sensor.status}
                    </div>

                    <div class="sensor-unit">
                        ${sensor.timestamp}
                    </div>
                `

                grid.appendChild(card)

            })

        })

    } catch(err) {

        console.error("Error loading sensors:", err)

    }
}

loadSensors()

setInterval(loadSensors, 5000)
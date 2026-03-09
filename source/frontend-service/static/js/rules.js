import { getRules, createRule, updateRule, deleteRule } from './api.js';

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function loadRules() {
    const rules = await getRules();
    const container = document.getElementById("rules");
    container.innerHTML = "";

    if (rules.length === 0) {
        container.innerHTML = `<div class="empty-state">No automation rules yet</div>`;
        return;
    }

    rules.forEach(r => {
        const id = "rule" + r.id;
        const card = document.createElement("div");
        card.className = "rule-card";

        card.innerHTML = `
        <div class="rule-title">
            <input id="${id}name" value="${r.name}">
        </div>
        <div class="rule-condition">
            IF
            <input id="${id}sensor_name" value="${r.sensor_name}">
            <input id="${id}metric_name" value="${r.metric_name}">
            <select id="${id}operator">
                <option ${r.operator == ">" ? "selected" : ""}>></option>
                <option ${r.operator == "<" ? "selected" : ""}><</option>
                <option ${r.operator == ">=" ? "selected" : ""}>>=</option>
                <option ${r.operator == "<=" ? "selected" : ""}><=</option>
                <option ${r.operator == "=" ? "selected" : ""}>=</option>
            </select>
            <input id="${id}threshold_value" type="number" value="${r.threshold_value}">
        </div>
        <div class="rule-action">
            THEN
            <input id="${id}actuator_name" value="${r.actuator_name}">
            <select id="${id}target_state">
                <option ${r.target_state == "ON" ? "selected" : ""}>ON</option>
                <option ${r.target_state == "OFF" ? "selected" : ""}>OFF</option>
            </select>
        </div>
        </div>
        <div class="button-container"> <!-- Contenitore per i pulsanti -->
            <button class="update-btn" id="${id}update">Update</button>
            <button class="rule-delete" id="${id}delete">✕</button>
        </div>
    `;

    container.appendChild(card);

        // Aggiornamento della regola
        document.getElementById(id + "update").onclick = async () => {
            const rule = {
                id: r.id,
                name: document.getElementById(id + "name").value,
                sensor_name: document.getElementById(id + "sensor_name").value,
                metric_name: document.getElementById(id + "metric_name").value,
                operator: document.getElementById(id + "operator").value,
                threshold_value: parseFloat(document.getElementById(id + "threshold_value").value),
                actuator_name: document.getElementById(id + "actuator_name").value,
                target_state: document.getElementById(id + "target_state").value
            };

            await updateRule(rule);
            sleep(3000).then(() => {
                loadRules();
            });
        };

        // Eliminazione della regola
        document.getElementById(id + "delete").onclick = async () => {
            await deleteRule(r.id);
            sleep(3000).then(() => {
                loadRules();
            });
        };
    });
}

// Invio del modulo per la creazione di una nuova regola
document.getElementById("ruleForm").onsubmit = async (e) => {
    e.preventDefault();

    const rule = {
        name: document.getElementById("name").value,
        sensor_name: document.getElementById("sensor").value,
        metric_name: document.getElementById("metric").value,
        operator: document.getElementById("operator").value,
        threshold_value: parseFloat(document.getElementById("threshold").value),
        actuator_name: document.getElementById("actuator").value,
        target_state: document.getElementById("state").value
    };

    await createRule(rule);
    sleep(3000).then(() => {
        loadRules();
    });
}

loadRules();
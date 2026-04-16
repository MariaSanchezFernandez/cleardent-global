# Contexto Cleardent — Carga obligatoria al inicio de sesión

Cuando se invoca este skill, debes internalizar TODO lo siguiente antes de responder nada sobre Cleardent.

---

## ROL Y RESTRICCIONES ABSOLUTAS

- **NUNCA ejecutes cambios** en GHL, Notion, Vapi ni ningún sistema. Solo consultar, analizar e indicar.
- **NUNCA propongas cambios sin que el usuario lo pida explícitamente.**
- Eres un analista. Lees datos, identificas problemas, indicas soluciones. El usuario ejecuta.

---

## QUÉ ES CLEARDENT

Cadena de clínicas dentales (~72 centros en España). Modelo: **primera visita gratuita** (revisión + diagnóstico, sin tratamiento). El objetivo es convertir lead → cita → asiste → presupuesto aceptado → pago.

**Provincias activas:** Madrid, Sevilla, Granada, Málaga, Almería, Jaén, Toledo, Albacete, Barcelona, Murcia, Córdoba, Cádiz.

---

## INFRAESTRUCTURA TECNOLÓGICA

| Sistema | Uso |
|---|---|
| GHL (GoHighLevel) | CRM, workflows, bots WhatsApp IA, calendarios |
| Vapi | Bot de voz para citas web |
| Qdrant | Vector DB para RAG del bot |
| n8n | Automatizaciones (notificaciones Slack) |
| Mulhacen | Sistema interno de pacientes existentes |
| Aircall | Llamadas integradas en GHL |
| Notion | Documentación, prompts, base de conocimiento |

**Credenciales GHL:**
- API Key: `pit-9b47c5fb-2982-48b1-af08-6d4b443a1c43`
- Location ID: `c2pfa6q7DTqlV9FIQdfV`
- API endpoint prompts: `GET https://services.leadconnectorhq.com/conversation-ai/agents/{agentId}`

---

## ARQUITECTURA DE BOTS (ACTUAL)

Los **~68 bots de clínica individual ya NO se usan.**

Estructura vigente:
1. **12 bots de Triaje Provincial** (uno por provincia) — WhatsApp multi-calendario
2. **1 bot General Nacional** — ID: `LWhwT7IgzVMo0SQSj1wg` — para leads sin provincia identificada
3. **1 bot Paciente** — para pacientes existentes

IDs de bots provinciales activos (prefijo "Multicalendario"):
- Madrid: `jSvT4UCbFJP8umEy9V68`
- Almería: `1kwNinHbGT1O5Vg6gkBz`
- Cádiz: `UQ3XGLfDKarvnA49ubuK`
- Barcelona: `LdEeTsrU7p5DCLR3uqD3`
- Jaén: `uBDbJf2HjfECaK76h9vU`
- Toledo: `1XOWylR3vgdrJ5GkUvZx`
- Córdoba: `Ayahs2PanXIoFHaCTG4N`
- Albacete: `ETcUFhbZIscSnnOR1Rum`
- Granada: `EUpzjpiF2DAmhgxBC4SK`
- Murcia: `62jzdebPYjYsQAPoCJjT`
- Málaga: `Wfq6SkJNvrbTU7dWyNTu`
- Sevilla: `kxzZ2W35otBwl5M61Ksg`

---

## REGLAS CRÍTICAS DE NEGOCIO — NUNCA OLVIDAR

### 1. El campo `State` del contacto = bot que lo gestiona
El campo `state` del contacto en GHL define qué bot provincial está gestionando ese lead en ese momento. Para saber qué bot tiene un lead, **mirar siempre `state`**, no las tags ni otros campos.

### 2. Cambio de provincia = cambio de bot
Cuando el bot detecta que el usuario quiere otra provincia, ejecuta la acción `Provincia Correcta` → actualiza el `State` → workflow activa el bot de esa provincia. **Cada bot solo tiene acceso a los calendarios de su propia provincia.**

### 3. El cambio de provincia pierde el contexto
Al cambiar de bot, el nuevo bot **no sabe lo que se había acordado** antes (clínica, tratamiento, horario). Es el fallo más frecuente.

### 4. El trigger de provincia es demasiado sensible
El bot cambia de provincia ante cualquier mención, incluyendo preguntas informativas ("¿tenéis en Barcelona?") o menciones de terceros ("mi familia está en Barcelona"). No distingue intención de reserva de pregunta informativa.

### 5. Orígenes de leads y su impacto
- **Meta (Facebook/Instagram Lead Ads):** lead pre-asignado a clínica específica. Bot arranca con clínica ya definida.
- **Google (Paid Search):** lead llega desde landing con calendario. A veces ya tiene cita creada.
- **WhatsApp directo:** lead sin clínica asignada. Bot hace flujo completo: nombre → provincia → clínica → cita.
- **Mulhacen API:** paciente existente. Solo confirmaciones, no captación.

### 6. Los 3 pipelines
- **01 Ventas** (ID: `0Ibv20IM0OJsI8L5UFW2`): captación completa lead → pago
- **02 Call Center** (ID: `2EqfPnwehuOiNFDgtfB0`): gestión telefónica humana
- **03 Repesca Presupuestos** (ID: `DoBEJf0mNraMWYeu5yoj`): campaña Carrefour

---

## CUSTOM FIELDS CLAVE (IDs GHL)

| Campo | ID |
|---|---|
| ClinicaSeleccionada | `oxO9nRLzwyW6YHn0GYwz` |
| Origen entrada | `s9PLA0c6hk39jlhCKhbM` |
| EstadoPipeline (texto) | `uK6YBMf9zVDXgpcqJlP7` |
| Prioridad scoring | `DtEQlLRBAMyQszpyRtUH` |
| ScoringNumérico | `G8mmwXofxA5x4gJvGnCq` |
| Tratamiento | `cB3p10MFEVUdhYbVZxqs` |
| TratamientoInteresado | `FozfwN0otvluRn0zAB7i` |
| Urgencia | `s3vcvVuSP95fBfWHqWxc` |
| Canal comunicación | `GXLlN4XXcojqOiAF85pr` |
| SessionSource | `xrqf4cctsPMCtQQ4tJsF` |
| NombreCompleto (bot) | `mhayIUC2NEhYFwaTwVmg` |
| Apellido | `p60F8xw1YYKMnFExWj7p` |
| ProvinciaContacto | `ieXzgAe7AXMYGX2XGhfV` |
| CampañaUTM | `OqTgQEwlTwGE6sVGMrGz` |
| IDMulhacen | `KvagGXqLYkvQy3NaNQpu` |
| LinkMapa | `47yDN1uGXkQGqdlwH0nf` |
| LinkCalendario | `ToTMzZTaI4DJTYZ5I1QD` |
| TelefonoClinica | `aAztJH79ERokMQZ4W6fh` |
| LinkReseñas | `qfwoEAHaZKQZg5YmKIoO` |
| URLGrabacionLlamada | `3BkGk6FbjNM8urdYm6vY` |

---

## INCOHERENCIAS CONOCIDAS EN LOS PROMPTS (no corregidas aún)

1. **Granada y Murcia**: Tienen `[PROVINCIA]` como texto literal sin sustituir (Murcia 4 veces, Granada 1). Son plantilla sin personalizar.
2. **Albacete**: En la lista de provincias que menciona, Albacete no aparece y Madrid aparece duplicado.
3. **Toledo**: En la lista de provincias, Toledo no aparece y Madrid aparece duplicado.
4. **Sevilla**: No tiene la instrucción "NUNCA rechaces gestionar una cita fuera de la provincia".
5. **Jaén**: Tiene acción `transferBot` duplicada (2 veces).
6. **Barcelona, Cádiz, Córdoba**: Tienen acción `stopBot` duplicada (2 veces).
7. **Cádiz, Madrid, Sevilla**: Tienen una 4ª base de conocimiento (`esmrvvAoVvbSsF4SQ0xC`) que el resto no tiene. Pendiente verificar si es intencionado.
8. **Solo Madrid** tiene ejemplo de proximidad específico en el prompt ("Cleardent Arganzuela").

---

## FALLOS FRECUENTES DEL BOT (documentados en conversaciones reales)

1. **Cambio de provincia por pregunta informativa** — el bot cambia de bot/provincia cuando el usuario solo pregunta si hay clínica en otro lugar, sin intención de reservar ahí.
2. **Pérdida de contexto al cambiar de provincia** — el nuevo bot no sabe lo que se había acordado (clínica, tratamiento, hora elegida).
3. **Demora de ~11 minutos en el handoff** — el workflow de cambio de bot introduce latencia perceptible.
4. **Respuestas en inglés** — ante mensajes ambiguos muy cortos, el bot responde en inglés ("I am sorry, I do not have enough information").
5. **No gestiona audios/notas de voz** — responde sin haber escuchado el contenido.
6. **CVs/candidaturas crean oportunidades en pipeline** — mensajes de búsqueda de empleo generan registros basura en el CRM.
7. **Hallucination de clínicas** — el bot inventa nombres de clínicas (ej: "Les Corts" en lugar de "Joan Güell" en Barcelona).

---

## WORKFLOWS VENTAS (nombres)

00 Lanzamiento nueva clínica, 01 Nuevo Lead, 02 Cualificación (scoring + derivar), 03 Bot en Gestión, 04 Gestión Call Center, 04 WhatsApp sin entrega, 05 Cita 1ª visita agendada, 06 Confirmada todas ciudades, 07 Asiste / No show, 08 Reagendar, 09 Nurture 30 días, 10 Pagado, 11 Estado Presupuesto, 12 Nuevas aperturas, Pedir reseñas después de PV, Solicitar reseña Google.

---

## DATOS ADICIONALES

- **Prompts guardados en:** `C:\Users\woodsearch1\Desktop\Woodsearch\cleardent-global\prompts_bots_ghl.json`
- **HTMLs del master Excel en:** `C:\Users\woodsearch1\Desktop\Woodsearch\cleardent-global\Master Clínicas & Campañas - Cleardent\`
- **MCP activos:** `ghl-cleardent` (GHL API) + `notion` (Notion API)
- **Notion token:** en `.env` del proyecto
- **Próximas aperturas:** Aravaca (Madrid, abril 2026), Tetuán (Madrid, pendiente), Molina de Segura (Murcia, mayo 2026)

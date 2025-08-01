# 🚀 Guida Deployment Produzione con Cloudflare

## 📋 Checklist Pre-Deploy

### 1. **Configurazione Ambiente**
```bash
# Copia il file di esempio delle variabili d'ambiente
cp .env.example .env

# Modifica le variabili per la produzione
nano .env
```

### 2. **Variabili d'Ambiente Essenziali**
```env
FLASK_ENV=production
SECRET_KEY=your-super-secret-256-bit-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
CLOUDFLARE_ONLY=true
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## 🌐 Deployment su Render/Railway/Heroku

### **Render (Consigliato)**
1. Connetti il repository GitHub
2. Imposta le variabili d'ambiente nel dashboard
3. Il `Procfile` gestirà automaticamente l'avvio
4. Comando build: `pip install -r requirements.txt`
5. Comando start: `gunicorn --config gunicorn.conf.py app:app`

### **Railway**
```bash
# Installa Railway CLI
npm install -g @railway/cli

# Login e deploy
railway login
railway deploy
```

### **Heroku**
```bash
# Installa Heroku CLI e fai login
heroku create your-app-name
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=postgresql://...

# Deploy
git push heroku main
```

---

## ☁️ Configurazione Cloudflare

### 1. **Setup Dominio**
1. Registra il dominio su Cloudflare
2. Cambia i nameserver del dominio con quelli di Cloudflare
3. Aspetta la propagazione DNS (max 24h)

### 2. **Record DNS**
```
Tipo: A
Nome: @
Valore: IP_DEL_TUO_SERVER
Proxy: ✅ Attivato (arancione)

Tipo: CNAME
Nome: www
Valore: your-domain.com
Proxy: ✅ Attivato
```

### 3. **SSL/TLS**
- **Modalità**: Full (Strict) se hai certificato sul server
- **Modalità**: Full se non hai certificato (Cloudflare fornisce HTTPS)
- **Edge Certificates**: Auto-generati da Cloudflare

### 4. **Security Settings**
```
Security Level: Medium/High
Bot Fight Mode: ✅ Attivato
Browser Integrity Check: ✅ Attivato
Hotlink Protection: ✅ Attivato
```

### 5. **Firewall Rules**
```javascript
// Blocca paesi sospetti (opzionale)
(ip.geoip.country in {"CN" "RU" "KP"})

// Rate limiting
(http.request.uri.path contains "/api/" and rate(10m) > 100)

// Blocca bot cattivi
(cf.threat_score >= 10)
```

### 6. **Page Rules**
```
https://yourdomain.com/assets/*
Cache Level: Cache Everything
Edge Cache TTL: 1 month

https://yourdomain.com/api/*
Cache Level: Bypass
Disable Apps: On
```

---

## 🔒 Hardening Sicurezza

### 1. **Variabili Obbligatorie**
```env
# Genera con: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=64-character-random-hex-string

# Solo IP Cloudflare (se vuoi massima sicurezza)
CLOUDFLARE_ONLY=true

# CORS restrittivo
CORS_ORIGINS=https://yourdomain.com
```

### 2. **Headers di Sicurezza** 
Il middleware automaticamente aggiunge:
- `Strict-Transport-Security`
- `Content-Security-Policy`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `X-XSS-Protection`

### 3. **Rate Limiting (Cloudflare)**
- API endpoints: 100 req/10min per IP
- Login/Register: 5 req/min per IP
- General: 1000 req/hour per IP

---

## 🧪 Testing

### **Test Locale con PostgreSQL**
```bash
docker-compose up -d
# App disponibile su http://localhost:8000
```

### **Test Produzione**
```bash
# Test SSL
curl -I https://yourdomain.com

# Test API
curl https://yourdomain.com/api/publisher/status

# Test Security Headers
curl -I https://yourdomain.com | grep -i security
```

---

## 📊 Monitoring

### **Cloudflare Analytics**
- Dashboard automatico con metriche traffico
- Security events e attacchi bloccati
- Performance insights

### **Application Monitoring**
```python
# Aggiungi a app.py per logging avanzato
import logging
logging.basicConfig(level=logging.INFO)

@app.after_request
def log_request(response):
    app.logger.info(f'{request.remote_addr} - {request.method} {request.path} - {response.status_code}')
    return response
```

---

## 🚨 Troubleshooting

### **Errore 520/521/522**
- Controlla che l'app risponda su `0.0.0.0:PORT`
- Verifica che il server sia raggiungibile dall'IP Cloudflare

### **Database Connection Error**
- Controlla `DATABASE_URL` format
- Per PostgreSQL su Heroku: usa `postgresql://` non `postgres://`

### **CORS Errors**
- Imposta `CORS_ORIGINS` correttamente
- Verifica che il dominio usi HTTPS

### **Asset 404**
- Controlla che tutti i file statici siano nel repository
- Verifica le route Flask per `/assets/`, `/components/`, etc.

---

## 🎯 Performance Ottimale

### **Cloudflare Optimizations**
- **Minify**: CSS, JS, HTML auto-minification
- **Rocket Loader**: Async JS loading
- **Mirage**: Image optimization
- **Polish**: Lossy/Lossless image compression

### **App Optimizations**
- Usa `gunicorn` con worker multipli
- Database connection pooling
- Cache per query frequenti
- Compress static assets

---

## ✅ Go-Live Checklist

- [ ] Domini puntano a Cloudflare
- [ ] SSL/TLS configurato (Full/Strict)
- [ ] Variabili d'ambiente impostate
- [ ] Database migrato
- [ ] Security headers attivi
- [ ] Rate limiting configurato
- [ ] Monitoring attivo
- [ ] Backup strategy definita
- [ ] Test completi passati

**🎉 La tua app è pronta per la produzione!**

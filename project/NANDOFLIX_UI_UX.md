# Nandoflix — Ajustes UI / UX Jellyfin (para recordar)

## Qué se puede tunear nativamente (sin plugins)

### Por usuario (en la UI)
- **Configuración → Display**
  - Tema: Oscuro / Claro / Auto (sistema)
  - Color acento (rojo Netflix, azul Disney, etc.)
  - Densidad: Compacta / Normal / Cómoda
  - Tamaño de fuente
- **Página Inicio → editar (icono lápiz ✏️)**
  - Reordena secciones (drag & drop)
  - Oculta las que no uses: “Sugerencias”, “Por género”, “Por estudio”, etc.
  - Deja solo lo útil: “Continúa viendo”, “Próximos episodios”, “Recién añadidos”, “Mis listas”
  - Vista por defecto: **Grid** (carteles) o **Lista**
- **Cada biblioteca → botón ⋮ → Display**
  - Orden por defecto: Fecha añadida ↓ / Título / Rating / Fecha estreno
  - Agrupar por: Carpeta / Género / Año / Álbum / Ninguno
  - Vista por defecto: Grid / Lista / Detalle

### Admin (Dashboard)
- **General → Home page sections** → qué secciones aparecen globalmente y en qué orden
- **Metadata → Savers** → desactiva *Chapter images* / *Thumbnail images* si el server va justo
- **Reproducción** → *Auto-play next*, *Skip intro*, *Mark played %*, *Default audio/subtitle language*
- **Usuarios → cada uno → Política de acceso** → restricciones por rating, pin parental, límites de dispositivos

## Atajos de teclado (web)
| Tecla | Acción |
|-------|--------|
| `Espacio` / `K` | Play / Pause |
| `F` | Fullscreen |
| `M` | Mute |
| `← / →` | Seek ±30 s |
| `Shift+← / Shift+→` | Seek ±10 s |
| `↑ / ↓` | Volumen ± |
| `J / L` | Seek ±10 s (alt) |
| `C` | Subtítulos on/off |
| `S` | Stop |
| `0-9` | Saltar al % (0=0%, 5=50%, 9=90%) |

## Plugins recomendados (Catálogo → Plugins → Repositorio comunitario)
| Plugin | Qué hace |
|--------|----------|
| **ThemePark** | Temas completos tipo Netflix, Disney+, HBO, Apple TV+ (un clic) |
| **Jellyscrub** | Preview de vídeo al pasar ratón por la barra de progreso |
| **Custom CSS** | Inyecta tu propio CSS sin tocar archivos del servidor |
| **Intros** | Detección automática de intros/credits para *Skip intro* |
| **Trakt** | Sincroniza visto/en progreso con Trakt.tv |
| **OPDS** | Catálogos de ebooks/comics vía OPDS |
| **AudioBookshelf** | Integración con AudioBookshelf |

## CSS mínimo “tipo Netflix” (si usas plugin Custom CSS)
```css
/* Redondea pósters, oculta etiquetas, acento rojo */
.card { border-radius: 8px; overflow: hidden; }
.cardLabel { display: none !important; }
:root { --theme-accent: #e50914; --theme-accent-text: #ffffff; }
.homeSection { padding: 0 1rem; }
```

## Atajos para vivir mejor
- App móvil/TV: activa **“Auto-play next”** + **“Skip intro”** en Configuración → Reproducción
- **Sync offline**: en móvil, mantén pulsado un item → “Descargar” (necesita transcodificar si no es compatible nativo)
- **Multi-usuario**: cada perfil tiene su *Continúa viendo*, favoritos, progreso, restricciones

## Notas de este proyecto
- **TDT** ya integrada en Live TV (576 canales, guía EPG)
- **IPTV Internacional** lista filtrada (ES/UK/US/JP + anime) en `http://192.168.1.128:8899/iptv_filtrado.m3u` → añadir como M3U Tuner en Live TV
- **Stremio + Real-Debrid** para películas/series bajo demanda (mejor calidad que IPTV)
- Anime con subs ES → **Stremio + Anime Kitsu / Comet / MediaFusion** (no por IPTV)

---
*Archivo: `~/Code/Nandflix/NANDOFLIX_UI_UX.md`*
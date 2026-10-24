# PedidoLab V0 · Misión 2 · Precios

**Curso:** Arquitectura I · Tema 3 Refactoring
**Pareja 02:** Andrés y Alejandro · rama `pareja_02`
**Zona principal:** `src/pedidolabs/precios.py`

> **Estado de este documento:** en la rama todavía no hay commits propios
> (`git log --oneline main..HEAD` sale vacío), y `git diff main...HEAD --stat`
> tampoco muestra cambios. Las secciones 1, 2, 4 y 8 describen el código actual
> y el plan. Las secciones 3, 5, 6 (después) y 7 quedan como **[PENDIENTE]**
> hasta que el refactoring esté commiteado.

---

## 1. Misión y estado inicial

`precios.py` calcula, según el tipo de cliente (`NORMAL`, `PREMIUM`, `CORPORATIVO`):

| Función | Responsabilidad |
|---|---|
| `calcular_descuento(cliente, subtotal)` | Monto del descuento |
| `descripcion_descuento(cliente, subtotal)` | Texto del descuento (`"Cliente PREMIUM: 15%"`) |
| `calcular_beneficio_fidelidad(cliente, total)` | Puntos de fidelidad (`total // divisor`) |
| `calcular_total_con_descuento(pedido)` | `subtotal - descuento` |

En `main` las reglas son estas:

| Tipo | Umbral | % alto | % base | Divisor fidelidad |
|---|---|---|---|---|
| NORMAL | — | 0 % | 0 % | 50 000 |
| PREMIUM | ≥ 500 000 | 15 % | 10 % | 25 000 |
| CORPORATIVO | ≥ 1 000 000 | 20 % | 12 % | 20 000 |
| desconocido | — | 0 % | 0 % | 0 puntos |

**Pregunta de la misión:** *¿Qué tendría que modificarse si mañana apareciera una
nueva política comercial?*

## 2. Diagnóstico

Las líneas corresponden a `git show main:src/pedidolabs/precios.py`.

**a) El mismo condicional por tipo se repite en 3 funciones** (Switch Statements)

- `calcular_descuento`: líneas 2–12
- `descripcion_descuento`: líneas 15–25
- `calcular_beneficio_fidelidad`: líneas 28–34

```python
if cliente.tipo == "NORMAL": ...
if cliente.tipo == "PREMIUM": ...
if cliente.tipo == "CORPORATIVO": ...
```

**b) Shotgun Surgery.** Para agregar un tipo de cliente hay que tocar las 3
funciones anteriores y, además, otros módulos que también conocen los tipos:

- `src/pedidolabs/envios.py:19`: `tipo_cliente in ("PREMIUM", "CORPORATIVO")` decide el envío gratis.
- `src/pedidolabs/reportes.py:30-35`: `if/elif` por tipo para contar clientes.

**c) Conocimiento duplicado.** Cada porcentaje aparece dos veces, una vez como número
y otra como texto, y nada obliga a que coincidan:

```python
return subtotal * 0.15          # línea 6
return "Cliente PREMIUM: 15%"   # línea 19
```

Lo mismo pasa con 0.10/"10%", 0.20/"20%" y 0.12/"12%". Los umbrales
`500_000` y `1_000_000` también están repetidos en las dos funciones.

**d) Primitive Obsession y números mágicos.**

- `Cliente.tipo` es un `str` (`cliente.py`), así que un error de tipeo como `"PREMIUN"` cae sin aviso en el "descuento 0".
- Los umbrales (`500_000`, `1_000_000`), los porcentajes y los divisores (`50_000`, `25_000`, `20_000`) son literales sin nombre.

[PENDIENTE: captura Sonar antes]

## 3. Red de seguridad

[PENDIENTE: `tests/test_precios_caracterizacion.py` no existe todavía en la rama.]

Las pruebas actuales (`tests/test_precios.py`) dejan estos huecos, que la
caracterización debería cubrir:

- `descripcion_descuento` para NORMAL, PREMIUM alto, CORPORATIVO (base y alto) y tipo desconocido.
- `calcular_beneficio_fidelidad` para NORMAL, CORPORATIVO y tipo desconocido (debe dar `0`).
- `calcular_descuento` con tipo desconocido (debe dar `0.0`).
- Bordes de umbral: `499_999` / `500_000` y `999_999` / `1_000_000`.
- `calcular_total_con_descuento` con un `Pedido` real.

## 4. Plan de refactoring y alternativa descartada

**Plan: una tabla de políticas.** Los tres tipos usan el mismo algoritmo
("si supera el umbral aplica el % alto, si no el % base; los puntos son
total // divisor"). Lo único que cambia son los **datos**:

```python
@dataclass(frozen=True)
class PoliticaCliente:
    umbral: float
    porcentaje_alto: float
    porcentaje_base: float
    divisor_fidelidad: int

    def porcentaje(self, subtotal):
        return self.porcentaje_alto if subtotal >= self.umbral else self.porcentaje_base

POLITICAS = {
    "NORMAL":      PoliticaCliente(0,         0.00, 0.00, 50_000),
    "PREMIUM":     PoliticaCliente(500_000,   0.15, 0.10, 25_000),
    "CORPORATIVO": PoliticaCliente(1_000_000, 0.20, 0.12, 20_000),
}
```

Con esto el texto (`f"{p:.0%}"`) sale del mismo número que el cálculo, y se
elimina la duplicación 0.15/"15%".

**Descartamos Strategy.** Strategy sirve cuando varía el **algoritmo**. Aquí
varían los **parámetros**, así que tres clases con el mismo método solo
agregarían jerarquía e indirección sin ganar nada.

**Strategy sí se justificaría** si una política necesitara lógica propia, por
ejemplo descuentos escalonados por tramos, reglas por fecha o campaña, o
dependencias de otros datos del pedido (categoría de producto, historial).
En ese caso `PoliticaCliente` se podría convertir en una interfaz sin cambiar
a quienes la usan.

## 5. Secuencia de refactorings

[PENDIENTE: `git log --oneline main..HEAD` está vacío. Cuando existan los commits,
agregar un ítem por commit con qué cambió y que terminó con `pytest` en verde.]

Estado actual verificado: `pytest` → **40 passed**.

## 6. Antes vs. después

**Antes (`main`):** una nueva política comercial obliga a modificar **3 funciones**
en `precios.py` (`calcular_descuento`, `descripcion_descuento`,
`calcular_beneficio_fidelidad`) y a mantener sincronizados los porcentajes
numéricos y los textuales.

**Después:** [PENDIENTE: confirmar cuando el refactoring esté commiteado. El
objetivo es que baste con **una entrada en `POLITICAS`**.]

**Fuera de alcance:** `envios.py` y `reportes.py` siguen conociendo los tipos de
cliente. Si la nueva política afecta el envío gratis o los reportes, esos módulos
también habría que tocarlos.

[PENDIENTE: captura Sonar después]

## 7. Evaluación crítica

[PENDIENTE: completar con el resultado real. Puntos a evaluar:]

- **Mejoras esperadas:** una sola fuente de verdad por política, nada de duplicación número/texto y umbrales con nombre.
- **Costos:** una clase nueva (`PoliticaCliente`), la indirección de buscar en `POLITICAS` y decidir qué pasa con los tipos desconocidos.
- **Próximo cambio que se facilita:** sacar `POLITICAS` a configuración o reemplazar `tipo: str` por un `Enum`, y reutilizar la tabla desde `envios.py` y `reportes.py`.

## 8. Cómo ejecutar

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
```

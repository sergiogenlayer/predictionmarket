# Informe de gastos de wallet (Ethereum + Base)

Genera un desglose de **a dónde ha ido el dinero** de una wallet: total enviado,
por destinatario, por categoría, por cadena y por mes, más el CSV completo de
movimientos con enlace a cada transacción.

Solo usa la librería estándar de Python 3 — no hace falta instalar nada.

## Uso normal (con API key de Etherscan)

Una sola key de Etherscan V2 sirve para Ethereum y Base (gratis en
<https://etherscan.io/apis>).

```bash
cd scripts/wallet_expenses
export ETHERSCAN_API_KEY=xxxxxxxx

# 1) Descargar la actividad (txs normales, internas y ERC-20 de ambas cadenas)
python3 wallet_report.py fetch \
  --address 0x4aDfd543c112171dCAdAc79cAe086094dBeb4348 \
  --data-dir wallet_data

# 2) Construir el informe
python3 wallet_report.py report \
  --address 0x4aDfd543c112171dCAdAc79cAe086094dBeb4348 \
  --data-dir wallet_data --out-dir wallet_report \
  --eth-price 3200 \
  --labels labels.json
```

Salida en `wallet_report/`:

| Fichero | Contenido |
| --- | --- |
| `report.md` | Resumen listo para enviar: totales, top destinatarios, categorías, meses |
| `movements.csv` | Todos los movimientos, con enlace a Etherscan/Basescan |
| `labels.suggested.json` | Direcciones que aún no tienen nombre — rellénalo y pásalo con `--labels` |

Flujo recomendado: ejecuta el informe una vez, abre `labels.suggested.json`,
pon nombre y categoría a cada destinatario (agencia, influencer, herramientas,
bridge, exchange…), guárdalo como `labels.json` y vuelve a ejecutar `report`.
El desglose por categoría es lo que hace el informe legible para alguien que no
mira blockchain.

## Sin API key: exportar el CSV desde el explorador

Etherscan y Basescan permiten descargar el CSV de una dirección
(*Download Page Data / Export CSV*, hasta 5.000 filas). Después:

```bash
python3 wallet_report.py import-csv --csv export-eth.csv  --chain 1    --action txlist
python3 wallet_report.py import-csv --csv export-base.csv --chain 8453 --action txlist
python3 wallet_report.py report --address 0x... --eth-price 3200
```

Nota: el CSV del explorador solo cubre transferencias nativas de ETH. Para
tokens (USDC, etc.) descarga también el export de *Token Transfers* o usa la API.

## Valoración en USD

- Stablecoins (USDC, USDT, DAI…) se valoran 1:1. EURC se valora 1,00 y conviene
  reexpresarlo al tipo EUR/USD si el importe es relevante.
- ETH/WETH se valoran con `--eth-price` (precio plano). Para precios por fecha,
  pasa `--price-file precios.csv` con cabecera `date,symbol,usd_price`; esa hoja
  tiene prioridad sobre todo lo demás.
- Cualquier token sin precio aparece listado aparte, en cantidad de token, y
  nunca se cuela en los totales en USD.

## Detalles

- Incluye transacciones internas (movimientos de ETH iniciados por contratos),
  que el listado principal del explorador no muestra.
- Las transacciones fallidas se excluyen de los totales pero se conservan en el
  CSV; su gas sí cuenta como coste, porque se pagó.
- El gas se agrega aparte, como coste operativo.
- `--chains` por defecto es `1,8453` (Ethereum y Base); acepta cualquier chain id
  soportado por Etherscan V2 si más adelante hay que añadir otra red.

import pyfiglet
import rich
from pypinyin import lazy_pinyin, Style
from pprint import pprint

# pprint(pyfiglet.FigletFont().getFonts())
from rich.panel import Panel
from rich.box import DOUBLE  # rich面板样式

# style = Style.NORMAL
# result = pyfiglet.figlet_format(f"{' '.join(lazy_pinyin('外设产品', style=style))}", font="small_slant")
# print(result)


# rich.print(Panel(f"[bold red]爬取被风控，请前往[京东任意商品页->商品评价]进行滑块验证", style="red", box=rich.box.DOUBLE, expand=False))

from django.shortcuts import render, redirect
from django.views import View
from .models import Cell

MAX_PIECES = 6

class IndexView(View):
    def get(self, request):
        # セルの情報を取得して盤面を作成
        cells = Cell.objects.filter(is_deleted=False)
        board:list = [[None for _ in range(3)] for _ in range(3)]
        for cell in cells:
            board[cell.row][cell.col] = cell.value

        # 勝敗判定
        winner:str|None = check_winner(board)
        is_draw:bool = (winner is None) and all(cell is not None for row in board for cell in row)
        
        # htmlに渡すデータを作成
        return render(request, 'marubatu/index.html', {
            'board': board,
            'winner': winner,
            'is_draw': is_draw
        })

    def post(self, request):
        # リセットボタンが押された場合return
        if 'reset' in request.POST:
            Cell.objects.all().delete()
            return redirect('index')
        
        # まったボタンが押された場合、created_atが一番新しいセルを削除
        if 'matta' in request.POST:
            if Cell.objects.exists():
                if Cell.objects.filter(is_deleted=True).count() > 0:
                    newest_cell = Cell.objects.filter(is_deleted=True).order_by('created_at').last()
                    newest_cell.is_deleted = False
                    newest_cell.save()
                Cell.objects.order_by('created_at').last().delete()
            return redirect('index')

        # 座標を取得
        row = int(request.POST.get('row'))
        col = int(request.POST.get('col'))

        # すでに値が入っていたらreturn
        if Cell.objects.filter(row=row, col=col, is_deleted=False).exists():
            return redirect('index') 
        
        # 偶数回目のクリックでO、奇数回目のクリックでXを入れる(DBに保存)
        if Cell.objects.count() % 2 == 0:
            value = 'O'
        else:
            value = 'X'
        Cell.objects.create(row=row, col=col, value=value)

        # レコードが6個を超えた場合、最も古いレコードを論理削除
        if Cell.objects.filter(is_deleted=False).count() > MAX_PIECES:
            oldest_cell = Cell.objects.filter(is_deleted=False).order_by('created_at').first()
            oldest_cell.is_deleted = True
            oldest_cell.save()

        
        return redirect('index')
    
def check_winner(board):
    lines:list[str] = []
    # 横
    for row in board:
        lines.append(row)
    # 縦
    for col in range(3):
        lines.append([board[row][col] for row in range(3)])
    # 斜め
    lines.append([board[i][i] for i in range(3)])
    lines.append([board[i][2 - i] for i in range(3)])

    for line in lines:
        if line[0] and all(cell == line[0] for cell in line):
            return line[0]

    return None

index = IndexView.as_view()

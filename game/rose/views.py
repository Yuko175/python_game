from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from .models import Board, DeckCard, ActionLog, Player
import random

# TODO: エラーが出るボタンは非活性化する/エラー文を表示する
# TODO: 0. 山札に戻さない
# TODO: 1. 騎士の作成(playerテーブル：騎士の数：領地の数(2つ合わせたのがコマの数))
# TODO: 2. 終了判定
# TODO: 3. 得点計算
# TODO: 4. 文字を全て線文字に変更(カーソルを合わせたら日本語)


MAX_HAND_CARD_NUMBER = 5  # 手札の最大枚数
BOARD_SIZE = 9 # 盤面のサイズ：奇数：通常9x9
KING_START_POSITION = BOARD_SIZE // 2
KNIGHT_COUNT = 4 # 騎士の数
DECK_CARD = [
            {'up': 0, 'down': 1, 'right': 0, 'left': 1, 'display': '↙'},
            {'up': 0, 'down': 2, 'right': 0, 'left': 2, 'display': '↙↙'},
            {'up': 0, 'down': 3, 'right': 0, 'left': 3, 'display': '↙↙↙'},
            {'up': 0, 'down': 0, 'right': 0, 'left': 1, 'display': '←'},
            {'up': 0, 'down': 0, 'right': 0, 'left': 2, 'display': '←←'},
            {'up': 0, 'down': 0, 'right': 0, 'left': 3, 'display': '←←←'},
            {'up': 1, 'down': 0, 'right': 0, 'left': 1, 'display': '↖'},
            {'up': 2, 'down': 0, 'right': 0, 'left': 2, 'display': '↖↖'},
            {'up': 3, 'down': 0, 'right': 0, 'left': 3, 'display': '↖↖↖'},
            {'up': 1, 'down': 0, 'right': 0, 'left': 0, 'display': '↑'},
            {'up': 2, 'down': 0, 'right': 0, 'left': 0, 'display': '↑↑'},
            {'up': 3, 'down': 0, 'right': 0, 'left': 0, 'display': '↑↑↑'},
            {'up': 0, 'down': 1, 'right': 0, 'left': 0, 'display': '↓'},
            {'up': 0, 'down': 2, 'right': 0, 'left': 0, 'display': '↓↓'},
            {'up': 0, 'down': 3, 'right': 0, 'left': 0, 'display': '↓↓↓'},
            {'up': 1, 'down': 0, 'right': 1, 'left': 0, 'display': '↗'},
            {'up': 2, 'down': 0, 'right': 2, 'left': 0, 'display': '↗↗'},
            {'up': 3, 'down': 0, 'right': 3, 'left': 0, 'display': '↗↗↗'},
            {'up': 0, 'down': 0, 'right': 1, 'left': 0, 'display': '→'},
            {'up': 0, 'down': 0, 'right': 2, 'left': 0, 'display': '→→'},
            {'up': 0, 'down': 0, 'right': 3, 'left': 0, 'display': '→→→'},
            {'up': 0, 'down': 1, 'right': 1, 'left': 0, 'display': '↘'},
            {'up': 0, 'down': 2, 'right': 2, 'left': 0, 'display': '↘↘'},
            {'up': 0, 'down': 3, 'right': 3, 'left': 0, 'display': '↘↘↘'},
        ]

class IndexView(View):
    def get(self, request):
        # Board、DeckCard、ActionLogが存在しない場合は新規作成
        self.initialize_DB()

        # Board、ActionLogを取得
        k_info = Board.objects.latest('count')
        previous_action = ActionLog.objects.latest('count')

        return render(request, 'rose/index.html', self.handle_update_context(k_info.row, k_info.col, previous_action.player, previous_action.player, message=None))

    def post(self, request):
        # 1つ前の王の位置を取得
        k_info = Board.objects.latest('count')
        previous_k_row = k_info.row
        previous_k_col = k_info.col

        # 1つ前のログを取得
        previous_action = ActionLog.objects.latest('count')
        previous_player = previous_action.player

        # 現在のプレイヤーを決定
        if previous_player == 'player1':
            current_player = 'player2'
        else:
            current_player = 'player1'
        current_count = previous_action.count + 1
        

        # リセット
        if 'reset' in request.POST:
            return self.get(request)

        # 山札からカードを引く
        if 'draw_deck' in request.POST:
            return self.handle_draw_deck(request, current_count, current_player, previous_player, previous_k_row, previous_k_col)

        # 手札からカードを出す
        if 'play_hand' in request.POST:
            return self.handle_play_hand(request, k_info, current_count, current_player, previous_player, previous_k_row, previous_k_col)

        # パス
        if 'pass' in request.POST:
            return self.handle_pass(request, current_count, current_player,previous_k_row, previous_k_col,previous_player)
        
        # エラー応答
        return HttpResponse("request.POST：エラー", status=404)

    # NOTE: 初期設定
    def initialize_DB(self):
        """初期設定する

        """
        # 削除
        Board.objects.all().delete()
        DeckCard.objects.all().delete()
        ActionLog.objects.all().delete()
        Player.objects.all().delete() 
        # 作成   
        Board.objects.create(id=1, row=KING_START_POSITION, col=KING_START_POSITION, count=0, player='start')
        self.create_deck_cards()
        ActionLog.objects.create(count=0, player=None, action=None)
        Player.objects.create(player='player1', knight_count=KNIGHT_COUNT)
        Player.objects.create(player='player2', knight_count=KNIGHT_COUNT)


    # NOTE: 盤面の状態を取得
    def get_board_detail(self):
        """盤面の状態を取得する
        Returns:
            list: 盤面の状態
        """
        board_detail = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for k in Board.objects.all():
            # FIXME: colとrowが逆になっている
            board_detail[k.col][k.row] = k.player
        return board_detail

    # NOTE: カード作成
    def create_deck_cards(self):
        """カードを作成する
        
        """
        for card in DECK_CARD:
            DeckCard.objects.create(
                up=card['up'],
                down=card['down'],
                right=card['right'],
                left=card['left'],
                display=card['display']
            )
            
    def handle_update_context(self, row, col, player, next_player,message=None):
        """画面のアップデートのハンドラ
        Args:
            row (int): 現在のkingの行
            col (int): 現在のkingの列
            player (str): 現在のプレイヤー
            next_player (str): 次のプレイヤー
            message (str): メッセージ
        Returns:
            dict: 画面のコンテキスト
        """
        can_play = self.can_play(row, col, next_player)
        if message is None:
            if can_play:
                message="アクションしてください"
            else:
                message="パスしてください"
        return self.update_context(row, col, player,can_play ,message)

    # NOTE: 画面アップデート
    def update_context(self, row, col, player,can_play,message):
        """contextのアップデート
        Args:
            row (int): 現在のkingの行
            col (int): 現在のkingの列
            player (str): 現在のプレイヤー
            can_play (bool): アクション可能かどうか
            message (str): メッセージ
        Returns:
            dict: 画面のコンテキスト
        """
        board_detail = self.get_board_detail()
        context = {
            'k_position': {'row': row, 'col': col},
            'board_detail': board_detail,
            'player': player,
            'deck_cards': DeckCard.objects.all(),
            'can_play': can_play,
            'message': message
        }
        return context
    
    #NOTE: アクション可能か判断する 
    def can_play(self, row, col, next_player):
        """ アクション可能か判断する 
        Args:
            row (int): 現在のkingの行
            col (int): 現在のkingの列
            next_player (str): 次のプレイヤー
        Returns:
            bool: アクション可能かどうか
        """
        # 手札の枚数、使用可能な手札の枚数、山札が空であるかどうかを確認
        hand_card_count = len(DeckCard.objects.filter(owner=next_player))
        playable_hand_count = len(self.get_playable_hand_cards(row, col, next_player))
        no_deck_cards = not DeckCard.objects.filter(owner__isnull=True).exists()
        
        # パスの条件をチェック
        if (hand_card_count >= MAX_HAND_CARD_NUMBER and playable_hand_count == 0) or\
            (no_deck_cards and playable_hand_count == 0):
            print(f"{next_player}はパス可能")
            return False
        else:
            print("アクション可能")
            return True

    # NOTE: 山札からカードを引く処理
    def handle_draw_deck(self, request, current_count, current_player, previous_player ,previous_k_row, previous_k_col):
        """山札からカードを引く処理
        Args:
            request (HttpRequest): リクエスト
            current_count (int): 現在のカウント
            current_player (str): 現在のプレイヤー
            previous_player (str): 1つ前のプレイヤー
            previous_k_row (int): 1つ前のkingの行
            previous_k_col (int): 1つ前のkingの列
        Returns:
            HttpResponse: レスポンス
        """
        # 使える山札を取得
        # available_cardsはis_card_drawnがFalseのカード
        available_cards = DeckCard.objects.filter(is_card_drawn=False)
        
        # 山札がない場合
        if not available_cards.exists():
            # 山札をリセット
            # ownerがnullのis_card_drawnをFalseにする
            DeckCard.objects.filter(owner__isnull=True).update(is_card_drawn=False)
            if not available_cards.exists():
                print("カード上限(山札がない)")
                message="カード上限(山札がない)"
                return render(request, 'rose/index.html', self.handle_update_context(previous_k_row, previous_k_col, previous_player, current_player,message))

        # 山札からカードを引く
        drawn_card = random.choice(available_cards)
        drawn_card.owner = current_player # １. owner
        available_numbers = self.get_available_card_numbers(drawn_card.owner)

        # 使えるカード番号がない場合(手札がMAX_HAND_CARD_NUMBER枚以上の場合)
        if not available_numbers:
            print(f"カード上限({MAX_HAND_CARD_NUMBER}枚)")
            message=f"カード上限({MAX_HAND_CARD_NUMBER}枚)"
            return render(request, 'rose/index.html', self.handle_update_context(previous_k_row, previous_k_col, previous_player,current_player,message))

        # 手札のカード番号を決定/手札の登録
        drawn_card.number = min(available_numbers) # ２. number
        drawn_card.is_card_drawn = True # ３. is_card_drawn
        drawn_card.save()# １.owner,　２.number, ３. is_card_drawnを保存

        # ログの記入
        ActionLog.objects.create(count=current_count, player=current_player, action='draw_deck')

        return render(request, 'rose/index.html', self.handle_update_context(previous_k_row, previous_k_col, current_player,  previous_player))

    # NOTE: 手札からカードを出す処理
    def handle_play_hand(self, request, k_info, current_count, current_player, previous_player, previous_k_row, previous_k_col):
        """ 手札からカードを出す処理
        Args:
            request (HttpRequest): リクエスト
            k_info (Board): 王様の情報
            current_count (int): 現在のカウント
            current_player (str): 現在のプレイヤー
            previous_player (str): 1つ前のプレイヤー
            previous_k_row (int): 1つ前のkingの行
            previous_k_col (int): 1つ前のkingの列
        Returns:
            HttpResponse: レスポンス
        """
        card_number = int(request.POST.get('card_number'))
        card_owner = request.POST.get('card_owner')
        hand_card = DeckCard.objects.get(owner=card_owner, number=card_number)
        
        # 新しい位置
        new_k_row = previous_k_row + hand_card.down - hand_card.up
        new_k_col = previous_k_col + hand_card.right - hand_card.left

        if self.is_playable_hand(hand_card, current_player, previous_k_row, previous_k_col):
            # TODO: 騎士のボタンが押されている場合　かつ　騎士の残機が0より大きい場合
            Board.objects.filter(row=new_k_row, col=new_k_col).delete()
            # TODO: 騎士のcountを減らす処理
        else:
            print("移動不可")
            message="移動不可"
            return render(request, 'rose/index.html', self.handle_update_context(previous_k_row, previous_k_col, previous_player, current_player,message))

        # 手札を使用済みに更新
        hand_card.owner = None
        hand_card.number = None
        hand_card.save()
        
        # FIXME: これのためにBoardを取得している
        # 盤面の更新
        k_info.count += 1
        k_info.player = card_owner
        Board.objects.create(row=new_k_row, col=new_k_col, count=k_info.count, player=k_info.player)
        
        # ログの記入
        ActionLog.objects.create(count=current_count, player=card_owner, action='play_hand')

        return render(request, 'rose/index.html', self.handle_update_context(new_k_row, new_k_col, card_owner,previous_player))

    # NOTE: パス処理
    def handle_pass(self, request, current_count, current_player,previous_k_row, previous_k_col,previous_player):
        """ パスの処理をする
        Args:
            request (HttpRequest): リクエスト
            current_count (int): 現在のカウント
            current_player (str): 現在のプレイヤー
            previous_k_row (int): 1つ前のkingの行
            previous_k_col (int): 1つ前のkingの列
            previous_player (str): 1つ前のプレイヤー
        Returns:
            HttpResponse: レスポンス
        """
        # 出せる手札がある場合
        if len(self.get_playable_hand_cards(previous_k_row, previous_k_col, current_player)) > 0:
            print("出せる手札があるのでパスできません")
            message="出せる手札があるのでパスできません"
            return render(request, 'rose/index.html', self.handle_update_context(previous_k_row, previous_k_col, previous_player, current_player,message))
        # 出せる手札がない場合
        # かつ山札がある場合
        # かつ手札がMAX_HAND_CARD_NUMBER枚以下の場合 = 山札から引ける場合
        elif DeckCard.objects.filter(owner__isnull=True).exists() and len(DeckCard.objects.filter(owner=current_player)) < MAX_HAND_CARD_NUMBER:
            print("山札をひけるのでパスできません")
            message="山札をひけるのでパスできません"
            return render(request, 'rose/index.html', self.handle_update_context(previous_k_row, previous_k_col, previous_player, current_player,message))
        # パス処理
        else:    
            ActionLog.objects.create(count=current_count, player=current_player, action='pass')
            print(f"{current_player}がパスしました")
            return render(request, 'rose/index.html', self.handle_update_context(previous_k_row, previous_k_col, current_player , previous_player)) 

    # NOTE: 移動可能か判断する
    def is_playable_hand(self, hand_card, current_player, previous_k_row, previous_k_col):
        """ 移動可能か判断する
        Args:
            hand_card (DeckCard): 手札
            current_player (str): 現在のプレイヤー
            previous_k_row (int): 1つ前のkingの行
            previous_k_col (int): 1つ前のkingの列
        Returns:
            bool: 移動可能かどうか
        """
        tmp_previous_k_row=previous_k_row
        tmp_previous_k_col=previous_k_col
        # 新しい位置を計算
        tmp_new_k_row = tmp_previous_k_row + hand_card.down - hand_card.up
        tmp_new_k_col = tmp_previous_k_col + hand_card.right - hand_card.left
        print(f"新しい位置：{tmp_new_k_col}, {tmp_new_k_row}")

        # ボードの端に到達したかチェック
        if tmp_new_k_row < 0 or tmp_new_k_row >= BOARD_SIZE or tmp_new_k_col < 0 or tmp_new_k_col >= BOARD_SIZE:
            print("ボードの端に到達")
            return False
        
        # 盤面にすでにコマがある場合
        if Board.objects.filter(row=tmp_new_k_row, col=tmp_new_k_col).exists():
            existing_board = Board.objects.get(row=tmp_new_k_row, col=tmp_new_k_col)
            # 相手のコマがある場合
            if existing_board.player != current_player:
                print(f"{existing_board.player} != {current_player}")
                print("すでに相手のコマがある")
                return True
            # 自分のコマがある場合
            else:
                print("すでに自分のコマがある")
                return False
            
        # 盤面にコマがない場合   
        else:
            return True
    

    # NOTE: カード番号の取得(手札の中で使われていないカード番号のリストを返却)
    def get_available_card_numbers(self, owner):
        """ 手札の中で使われていないカード番号を取得する
        Args:
            owner (str): プレイヤー
        Returns:
            list: 使用可能なカード番号のリスト
        """
        available_numbers = []
        for number in range(MAX_HAND_CARD_NUMBER):
            if not DeckCard.objects.filter(owner=owner, number=number).exists():
                available_numbers.append(number)
        return available_numbers

    # NOTE: プレイ可能な手札
    def get_playable_hand_cards(self,  previous_k_row, previous_k_col, next_player):
        """ プレイ可能な手札を取得する
        Args:
            previous_k_row (int): 1つ前のkingの行
            previous_k_col (int): 1つ前のkingの列
            next_player (str): 次のプレイヤー
        Returns:
            list: プレイ可能な手札のリスト
        """
        playable_hand_cards=[]
        # previous_player(next_player)の使用可能な手札を取得
        for hand_card in DeckCard.objects.filter(owner = next_player):
            if self.is_playable_hand(hand_card, next_player,previous_k_row, previous_k_col):
                playable_hand_cards.append(hand_card.number)
        print(f"{next_player}の使用可能なカード：{playable_hand_cards}")
        return playable_hand_cards

index = IndexView.as_view()
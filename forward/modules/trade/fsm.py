# -*- encoding: utf-8 -*-

__author__ = 'Mohanson'

class Error(Exception):
    pass


class ErrorTrading(Error):
    def __init__(self, des):
        self.des = des

    def __str__(self):
        return self.des


class TradingAction(object):
    def __init__(self, action):
        self.action = action

    def __str__(self):
        return self.action

    def __hash__(self):
        return hash(self.action)

# 用户取消订单
TradingAction.CancelOrder = TradingAction('CancelOrder')
# 用户付款
TradingAction.Payment = TradingAction('Payment')
# 用户选择付款方式-快递
TradingAction.ChooseReceiptExpress = TradingAction('ChooseReceiptExpress')
# 商家配送
TradingAction.MerchantExpress = TradingAction('MerchantExpress')
# 用户收货
TradingAction.UserGetExpress = TradingAction('UserGetExpress')
# 用户选择付款方式-到店自提
TradingAction.ChooseReceiptPickup = TradingAction('ChooseReceiptPickup')
# 用户到店自提
TradingAction.Pickup = TradingAction('Pickup')
# 用户选择付款方式-到店消费
TradingAction.ChooseReceiptConsumption = TradingAction('ChooseReceiptConsumption')
# 用户到店消费
TradingAction.ConsumptionInShop = TradingAction('ConsumptionInShop')


class RefundAction(object):
    def __init__(self, action):
        self.action = action

    def __str__(self):
        return self.action

    def __hash__(self):
        return hash(self.action)

# 用户申请退款
RefundAction.UserApplyRefund = TradingAction('UserApplyRefund')
# 用户申请退货
RefundAction.UserApplyRefundGood = TradingAction('UserApplyRefundGood')
# 商家接受退货
RefundAction.MerchantAcceptRefundGood = TradingAction('MerchantAcceptRefundGood')
# 商家拒绝退货
RefundAction.MerchantRefusedRefundGood = TradingAction('MerchantRefusedRefundGood')
# 平台拒绝退款
RefundAction.PlatformRefusedRefund = TradingAction('PlatformRefusedRefund')
# 平台确认退款
RefundAction.PlatformAcceptRefund = TradingAction('PlatformAcceptRefund')
# 用户发货
RefundAction.UserExpressGood = TradingAction('UserExpressGood')
# 商家收货
RefundAction.MerchantGetExpress = TradingAction('MerchantGetExpress')
# 商家确认退款
RefundAction.MerchantAcceptRefund = TradingAction('MerchantAcceptRefund')
# 商家拒绝退款
RefundAction.MerchantRefusedRefund = TradingAction('MerchantRefusedRefund')
# 用户/商家确认已经退款成功
RefundAction.MerchantOrUserComfirmRefundSuccess = TradingAction('MerchantOrUserComfirmRefundSuccess')
# 用户/商家确认退款失败, 原因?
RefundAction.MerchantOrUserComfirmRefundFailed = TradingAction('MerchantOrUserComfirmRefundFailed')


class TradingState(object):
    def __init__(self):
        self.transitions = None

    def run(self, *args):
        pass

    def next(self, input):
        if input in self.transitions:
            return self.transitions[input]
        else:
            raise ErrorTrading('TradingAction is not support for this state')


class TradingStateInit(TradingState):
    # 用户已下单, 等待付款
    def run(self, *args):
        print('用户已下单, 等待付款')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                TradingAction.CancelOrder: TradingStateMechine.TradingStateClose,
                TradingAction.Payment: TradingStateMechine.TradingStatePayed,
            }
        return TradingState.next(self, input)


class TradingStateClose(TradingState):
    # 用户未付款, 交易关闭
    def run(self, *args):
        print('用户未付款, 交易关闭')


class TradingStatePayed(TradingState):
    # 用户已付款
    def run(self, *args):
        print('用户已付款')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                TradingAction.ChooseReceiptExpress: TradingStateMechine.TradingStateWaitExpress,
                TradingAction.ChooseReceiptPickup: TradingStateMechine.TradingStateWaitPickup,
                TradingAction.ChooseReceiptConsumption: TradingStateMechine.TradingStateWaitConsumption
            }
        return TradingState.next(self, input)


class TradingStateWaitExpress(TradingState):
    # 已付款, 待配送
    def run(self, *args):
        print('已付款, 待配送')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                TradingAction.MerchantExpress: TradingStateMechine.TradingStateWaitExpress,
                RefundAction.UserApplyRefund: RefundStateMechine.RefundStateWaitMerchantAuditRefund
            }
        return TradingState.next(self, input)


class TradingStateWaitPickup(TradingState):
    # 已付款, 等待用户到店自提
    def run(self, *args):
        print('已付款, 等待用户到店自提')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                TradingAction.Pickup: TradingStateMechine.TradingStatePickupDone,
                RefundAction.UserApplyRefund: RefundStateMechine.RefundStateWaitMerchantAuditRefund
            }
        return TradingState.next(self, input)


class TradingStateWaitConsumption(TradingState):
    # 已付款, 等待到店消费
    def run(self, *args):
        print('已付款, 等待到店消费')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                TradingAction.ConsumptionInShop: TradingStateMechine.TradingStateWaitPickup,
                RefundAction.UserApplyRefund: RefundStateMechine.RefundStateWaitPlatformAuditRefund
            }
        return TradingState.next(self, input)


class TradingStateUserWaitExpress(TradingState):
    # 配送中, 用户等待快递
    def run(self, *args):
        print('配送中, 用户等待快递')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                TradingAction.UserGetExpress: TradingStateMechine.TradingStateExpressDone,
                RefundAction.UserApplyRefund: RefundStateMechine.RefundStateWaitMerchantAuditRefund
            }
        return TradingState.next(self, input)


class TradingStatePickupDone(TradingState):
    # 用户已到店取货
    def run(self, *args):
        print('用户已到店取货')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                RefundAction.UserApplyRefundGood: RefundStateMechine.RefundStateWaitMerchantAuditRefundGood
            }
        return TradingState.next(self, input)


class TradingStateConsumptionDone(TradingState):
    # 用户已到店消费
    def run(self, *args):
        print('用户已到店消费')


class TradingStateExpressDone(TradingState):
    # 已快递收货, 交易完成
    def run(self, *args):
        print('用户已到店消费')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                RefundAction.UserApplyRefundGood: RefundStateMechine.RefundStateWaitMerchantAuditRefundGood
            }
        return TradingState.next(self, input)


class TradingStateRefundingSuccess(TradingState):
    # 退货/退款成功, 交易关闭
    def run(self, *args):
        print('退货/退款成功, 交易关闭')


class RefundState(object):
    def __init__(self):
        self.transitions = None

    def run(self, *args):
        pass

    def next(self, input):
        if input in self.transitions:
            return self.transitions[input]
        else:
            raise ErrorTrading('RefundAction is not support for this state')


class RefundStateWaitPlatformAuditRefund(RefundState):
    # 等待平台审核是否接受退款
    def run(self, *args):
        print('等待平台审核是否接受退款')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                RefundAction.PlatformAcceptRefund: RefundStateMechine.RefundStateRefunding,
                RefundAction.PlatformRefusedRefund: RefundStateMechine.RefundStateRefundNotPassByPlatform,
            }
        return RefundState.next(self, input)


class RefundStateWaitMerchantAuditRefundGood(RefundState):
    # 用户已提交退货申请, 等待商家审核
    def run(self, *args):
        print('用户已提交退货申请, 等待商家审核')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                RefundAction.MerchantAcceptRefundGood: RefundStateMechine.RefundStateWaitUserExprssGood,
                RefundAction.MerchantRefusedRefundGood: RefundStateMechine.RefundStateMerchantRefusedRefundGoodDone,
            }
        return RefundState.next(self, input)


class RefundStateWaitUserExprssGood(RefundState):
    # 商家接受用户退货, 等待用户发货
    def run(self, *args):
        print('商家接受用户退货, 等待用户发货')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                RefundAction.UserExpressGood: RefundStateMechine.RefundStateWaitMerchantAcceptGood,
            }
        return RefundState.next(self, input)


class RefundStateWaitMerchantAuditRefund(RefundState):
    # 用户已提交退款申请, 等待商家审核
    def run(self, *args):
        print('用户已提交退款申请, 等待商家审核')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                RefundAction.MerchantAcceptRefund: RefundStateMechine.RefundStateRefunding,
                RefundAction.MerchantRefusedRefund: RefundStateMechine.RefundStateMerchantRefusedRefundDone
            }
        return RefundState.next(self, input)


class RefundStateWaitMerchantAcceptGood(RefundState):
    # 用户已经发货, 等待商家收获
    def run(self, *args):
        print('用户已经发货, 等待商家收获')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                RefundAction.MerchantGetExpress: RefundStateMechine.RefundStateMerchantHasAcceptGood,
            }
        return RefundState.next(self, input)


class RefundStateMerchantRefusedRefundGoodDone(RefundState):
    # 商家拒绝退货申请
    def run(self, *args):
        print('商家拒绝退货申请')


class RefundStateMerchantHasAcceptGood(RefundState):
    # 商家已收获, 等待商家确认退款
    def run(self, *args):
        print('商家已收获, 等待商家确认退款')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                RefundAction.MerchantAcceptRefund: RefundStateMechine.RefundStateRefunding,
            }
        return RefundState.next(self, input)


class RefundStateMerchantRefusedRefundDone(RefundState):
    # 商家已经拒绝退款申请
    def run(self, *args):
        print('商家已经拒绝退款申请')


class RefundStateRefunding(RefundState):
    # 正在退款中
    def run(self, *args):
        print('正在退款中')

    def next(self, input):
        if not self.transitions:
            self.transitions = {
                RefundAction.MerchantOrUserComfirmRefundSuccess: RefundStateMechine.RefundStateRefundSuccess,
                RefundAction.MerchantOrUserComfirmRefundFailed: RefundStateMechine.RefundStateRefundFailed,
            }
        return RefundState.next(self, input)


class RefundStateRefundSuccess(RefundState):
    # 退款成功, 退款流程结束
    def run(self, *args):
        print('退款成功, 退款流程结束')


class RefundStateRefundFailed(RefundState):
    # 退款失败
    def run(self, *args):
        print('退款失败')


class RefundStateRefundNotPassByPlatform(RefundState):
    # 退款审核不通过
    def run(self, *args):
        print('退款审核不通过')


class TradingStateMechine(object):
    def __init__(self, init_state):
        self.state = init_state
        self.state.run()

    def run(self, input, *args):
        self.state = self.state.next(input)
        self.state.run(*args)
        return self.state


class RefundStateMechine(object):
    def __init__(self, init_state):
        self.state = init_state
        self.state.run()

    def run(self, input, *args):
        self.state = self.state.next(input)
        self.state.run(*args)
        return self.state


TradingStateMechine.TradingStateInit = TradingStateInit()
TradingStateMechine.TradingStateClose = TradingStateClose()
TradingStateMechine.TradingStatePayed = TradingStatePayed()
TradingStateMechine.TradingStateWaitExpress = TradingStateWaitExpress()
TradingStateMechine.TradingStateWaitPickup = TradingStateWaitPickup()
TradingStateMechine.TradingStateWaitConsumption = TradingStateWaitConsumption()
TradingStateMechine.TradingStateUserWaitExpress = TradingStateUserWaitExpress()
TradingStateMechine.TradingStatePickupDone = TradingStatePickupDone()
TradingStateMechine.TradingStateConsumptionDone = TradingStateConsumptionDone()
TradingStateMechine.TradingStateExpressDone = TradingStateExpressDone()
TradingStateMechine.TradingStateRefundingSuccess = TradingStateRefundingSuccess()

RefundStateMechine.RefundStateWaitPlatformAuditRefund = RefundStateWaitPlatformAuditRefund()
RefundStateMechine.RefundStateWaitMerchantAuditRefundGood = RefundStateWaitMerchantAuditRefundGood()
RefundStateMechine.RefundStateWaitUserExprssGood = RefundStateWaitUserExprssGood()
RefundStateMechine.RefundStateWaitMerchantAuditRefund = RefundStateWaitMerchantAuditRefund()
RefundStateMechine.RefundStateWaitMerchantAcceptGood = RefundStateWaitMerchantAcceptGood()
RefundStateMechine.RefundStateMerchantRefusedRefundGoodDone = RefundStateMerchantRefusedRefundGoodDone()
RefundStateMechine.RefundStateMerchantHasAcceptGood = RefundStateMerchantHasAcceptGood()
RefundStateMechine.RefundStateMerchantRefusedRefundDone = RefundStateMerchantRefusedRefundDone()
RefundStateMechine.RefundStateRefunding = RefundStateRefunding()
RefundStateMechine.RefundStateRefundSuccess = RefundStateRefundSuccess()
RefundStateMechine.RefundStateRefundFailed = RefundStateRefundFailed()
RefundStateMechine.RefundStateRefundNotPassByPlatform = RefundStateRefundNotPassByPlatform()

STATE_DEFINE = {
    '1': TradingStateMechine.TradingStateInit,
    '2': TradingStateMechine.TradingStateWaitExpress,
    '3': TradingStateMechine.TradingStateUserWaitExpress,
    '4': TradingStateMechine.TradingStateWaitConsumption,
    '5': TradingStateMechine.TradingStateWaitPickup,
    '6': TradingStateMechine.TradingStateExpressDone,
    '7': TradingStateMechine.TradingStateConsumptionDone,
    '8': RefundStateMechine.RefundStateWaitMerchantAuditRefund,
    '9': RefundStateMechine.RefundStateWaitUserExprssGood,
    '10': RefundStateMechine.RefundStateRefunding,
    '11': RefundStateMechine.RefundStateMerchantHasAcceptGood,
    '12': RefundStateMechine.RefundStateMerchantRefusedRefundGoodDone,
    '13': RefundStateMechine.RefundStateWaitPlatformAuditRefund,
    '14': RefundStateMechine.RefundStateRefundFailed,
    '15': RefundStateMechine.RefundStateRefunding,
    '16': RefundStateMechine.RefundStateRefundSuccess,
    '17': RefundStateMechine.RefundStateRefundFailed,
}


def bstatus_2_status(bstatus):
    return STATE_DEFINE[str(bstatus)]


def trading_state_mechine(bstatus):
    return TradingStateMechine(bstatus_2_status(bstatus))


if __name__ == '__main__':
    f = TradingStateMechine(bstatus_2_status(5))
    f.run(TradingAction.Pickup)
    f.run(RefundAction.UserApplyRefundGood)
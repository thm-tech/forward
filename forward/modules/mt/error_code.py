# -*- encoding: utf-8 -*-


class MtErrorCodeBase:

    def __init__(self, error_code):

        self.code = error_code
        self.des = None

    def __repr__(self):
        return self.code


class MTERROR:

    def __init__(self):
        pass

    UnKnowError = MtErrorCodeBase(0x00030000)
    UnKnowError.des = 'Don\'t ask me, I also don\'t know why it happend'

    MultipleResultsFound = MtErrorCodeBase(0x00030001)
    MultipleResultsFound.des = 'This instance should be only one in db, but founded more than one'

    NoResultFound = MtErrorCodeBase(0x00030002)
    NoResultFound.des = 'This instance should be only one in db, but founded None'

    MissingArgument = MtErrorCodeBase(0x00030003)
    MissingArgument.des = 'Missing argument what is necessary, You should read API file'

    AccountAlreadyExist = MtErrorCodeBase(0x00030004)
    AccountAlreadyExist.des = 'Cannot sign because account are already exist'

    ShopAndMerchantShouldOneToOne = MtErrorCodeBase(0x00030005)
    ShopAndMerchantShouldOneToOne.des = 'Shop and merchant should be one to one'

    FileTypeError = MtErrorCodeBase(0x00030006)
    FileTypeError.des = 'Uploaded File are illeagle'

    FileSizeError = MtErrorCodeBase(0x00030007)
    FileSizeError.des = 'Uploaded File are too big'

    ModifyPasswordError = MtErrorCodeBase(0x00030008)
    ModifyPasswordError.des = 'Please input right password'

    PasswordCheckError = MtErrorCodeBase(0x00030009)
    PasswordCheckError.des = 'Password type error'

    AuthError = MtErrorCodeBase(0x00030010)
    AuthError.des = 'AUTH fail!'

    RegisterFailed = MtErrorCodeBase(0x00030011)
    RegisterFailed.des = 'Merchant Register Failed due to some error in database, you should not blame me ...~_~...'

    MerchantIsExist = MtErrorCodeBase(0x00030012)
    MerchantIsExist.des = 'Mercahnt is existes!'

    DeleteActivityBeforeEndTime = MtErrorCodeBase(0x00030013)
    DeleteActivityBeforeEndTime.des = 'can not delete activity before activity endtime'
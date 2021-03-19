from model import StyleTransferModel
#from telegram_token import token
from io import BytesIO

# В бейзлайне пример того, как мы можем обрабатывать две картинки, пришедшие от пользователя.

model = StyleTransferModel()
first_image_file = {}
state = 0
def send_prediction_on_photo(update, context):
    #in order to perform style transfer we need to get two pictures. Each picture comes in every update
    #so, in the easiest case, we will keep id of the first picture in memory and when the second picture
    #comes we can load both images and process them.
    chat_id = update.message.chat_id
    print("Got image from {}".format(chat_id))

    # retrieving picture information
    image_info = update.message.photo[-1]
    image_file = context.bot.get_file(image_info)

    if chat_id in first_image_file:
        #the first picture gonna be content image, the second - style image
        content_image_stream = BytesIO()
        first_image_file[chat_id].download(out=content_image_stream)
        del first_image_file[chat_id]

        style_image_stream = BytesIO()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Style Image Loaded, processing... ")
        image_file.download(out=style_image_stream)

        output = model.transfer_style(content_image_stream, style_image_stream)

        # let's send photo back to chat
        output_stream = BytesIO()
        output.save(output_stream, format='PNG')
        output_stream.seek(0)
        context.bot.send_photo(chat_id, photo=output_stream)
        print("Sent Photo to user")
        state = 0
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Content Image Loaded, now load your Style Image")
        state = 1
        first_image_file[chat_id] = image_file

def start(update, context):
    if state==0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Send your Content Image!")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please refer to the last message!!!")
if __name__ == '__main__':
    from telegram.ext import Updater, MessageHandler, Filters
    import logging
    #Turning on the very basic logging to see error messages
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    updater = Updater(token='Enter your tg bot token here', use_context=True)

    dispatcher = updater.dispatcher
    if state==0:

    # WHen constructing complicated dialogs it would be better to use Conversation Handler
    # instead of using handlers this way
        photo_handler = MessageHandler(Filters.photo, send_prediction_on_photo)
    dispatcher.add_handler(photo_handler)

    start_handler = MessageHandler(Filters.text & (~Filters.command), start)
    dispatcher.add_handler(start_handler)
    updater.start_polling()

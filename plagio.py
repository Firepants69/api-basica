#archivo interfaces


class ImageScaler(ABC):

    @staticmethod
    @abstractmethod
    def scale(dimensions_to_scale,image):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def scale_without_deforming(dimensions_to_scale, image):
        raise  NotImplementedError


class ImageFetcher(ABC):

    @staticmethod
    @abstractmethod
    def get_random_images(number_of_images,path):
        raise NotImplementedError


class ImagePoster(ABC):
    @abstractmethod
    def post_image(self,image_path,text):
        raise NotImplementedError


# Image manager archivo




class ImageManager(ImageScaler):


    @staticmethod
    def scale(dimensions_to_scale,image):
        scale_image = image.copy()
        return scale_image.resize(dimensions_to_scale)

    @staticmethod
    def scale_without_deforming(dimensions_to_scale,image):
        scale_image = image.copy()
        scale_image.thumbnail(dimensions_to_scale)
        return  scale_image

    @staticmethod
    def put_watermark(meme,water_mark):
        rescale_tuple = (meme.size[0]//6,meme.size[1]//6)
        scale_water_mark = ImageManager.scale_without_deforming(rescale_tuple,water_mark)

        scale_water_mark.putalpha(64)
        wm_w,wm_h = scale_water_mark.size
        bg_w,bg_h = meme.size

        offset = ((bg_w - wm_w)//2,(bg_h - wm_h) //2)
        meme.paste(scale_water_mark,offset,scale_water_mark)


#archivo Template

from App.ImageManager import ImageManager


class Template:
    def __init__(self,place_images,template_image):
        self.__place_image = place_images
        self.__template_image = template_image


    def fill_template(self,images):
        filled_template = self.__template_image.copy()
        i = 0
        for place in self.__place_image:
            rescale_image = ImageManager.scale(place["scale"],images[i])
            filled_template.paste(rescale_image,place["location"])
            i+=1

        return filled_template


    def __len__(self):
       return  len(self.__place_image)



#archivo MemeGenerator

class MemeGenerator:
    templates = []

    def __init__(self,templates,images_path,memes_path,water_mark):
        self.templates = templates
        self.images_path = images_path
        self.memes_path = memes_path
        self.water_mark = water_mark

    def generate_meme(self):
        template = random.choice(self.templates)
        meme = template.fill_template(FetchRandomImages.get_random_images(len(template),self.images_path))
        ImageManager.put_watermark(meme= meme, water_mark= self.water_mark)
        return meme

    def generate_and_save_meme(self):
        meme = self.generate_meme()
        path = f"{self.memes_path}{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}.jpg"
        meme.save(path)
        return path

#archivo Twitter Manager

from itertools import count

import tweepy
from App.Interfaces import ImagePoster, ImageFetcher
class TweetManager(ImagePoster):



    def __init__(self, api_key, api_key_secret, bearer_token, access_token, access_token_secret):

        self.__api_key = api_key
        self.__api_key_secret = api_key_secret
        self.__bearer_token = bearer_token
        self.__access_token = access_token
        self.__access_token_secret = access_token_secret

        auth = tweepy.OAuth1UserHandler(api_key, api_key_secret, access_token, access_token_secret)
        self._api = tweepy.API(auth, wait_on_rate_limit=True)

        self._client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_key_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )

    def post_text(self, text):
        self._client.create_tweet(text=text)
        print("Se ha twitteado.")

    def post_image(self, image_path, text):
        # Subir la imagen utilizando la API v1.1
        media = self._api.media_upload(image_path)
        media_id = media.media_id_string
        # Crear el tweet con la imagen utilizando la API v2
        self._client.create_tweet(text=text, media_ids=[media_id])
        print("Se ha twitteado con imagen.")




#archivo RedditManager

from http.client import responses

import praw
import requests
from App.Interfaces import ImagePoster


class RedditManager(ImagePoster):

    def __init__(self,client_id,client_secret,user_agent,username,password):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__user_agent = user_agent
        self.__username = username
        self.__password = password

        self.__reddit = praw.Reddit(
            client_id = client_id,
            client_secret = client_secret,
            user_agent = user_agent,
            username = username,
            password = password
        )


    def post_image(self,image_path,text):
        print("se publicó el meme en reddit")


    def get_random_images(self, number_of_images, subreddit_name):
        print(f"{number_of_images} imagenes obtenidas de {subreddit_name}")


#archivo MemeBot

from App.Interfaces import ImagePoster
from App.MemeGenerator import MemeGenerator


class MemeBot:
    def __init__(self,tweet_manager,images_path,memes_path,templates,reddit_manager,water_mark):
        self.__tweet_manager = tweet_manager
        self.__images_path = images_path
        self.__memes_path = memes_path
        self.__templates = templates
        self.__reddit_manager = reddit_manager
        self.water_mark = water_mark

    def post_image_on_twitter(self):
        generator = MemeGenerator(memes_path=self.__memes_path,templates=self.__templates,images_path=self.__images_path,water_mark =water_mark)
        meme_path = generator.generate_and_save_meme()
        meme_name = meme_path[meme_path.rfind("/") + 1:meme_path.find(".jpng") - 3]
        self.__tweet_manager.post_image(image_path= meme_path,text = f"momo: {meme_name}" )

    def post_image_on_reddit(self):
        self.__reddit_manager.post_image()







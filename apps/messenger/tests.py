from channels.testing import ChannelsLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from seleniumlogin import force_login
from django.test import  TestCase
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
import time

from supports.models import School
from teachers.models import Teacher
from messenger.models import ChatGroup, Member, Message
from messenger.views import ChatsListView
from messenger.forms import ConversationForm


class TestViews(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="test1_user",
            password="test123456",
            user_type="SS",
            first_name="test",
            last_name="user",
        )
        self.school_1 = School.objects.create(name="Test", support=user)
        super().setUp()
        
    def test_chats_list_view(self):
        self.client.force_login(self.school_1.support)
        
        url = reverse("messenger:home")
        self.assertEqual(url, "/messenger/")
        self.assertEqual(resolve(url).func.__name__, ChatsListView.__name__)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset({"nav_color": "bg-dark"}, response.context)
        self.assertTemplateUsed(response, "dashboard/messenger/chats_list.html")
        self.assertTemplateNotUsed(response, "dashboard/messenger/chat_page.html")
        
    def test_create_group_successfully(self):
        self.client.force_login(self.school_1.support)
        
        self.assertEqual(ChatGroup.objects.count(), 0)
        url = reverse("messenger:home")
        data = {
            "conversation_type": "group",
            "name": "Test Group",
            "owner": self.school_1.support,
            "bio": "This is a test group",
        }
        response = self.client.post(url, data)
        messages = [*get_messages(response.wsgi_request)]
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, ChatGroup.objects.last().get_absolute_url())
        self.assertEqual(str(messages[-1]), "Group created successfully.")
        self.assertEqual(ChatGroup.objects.count(), 1)
        self.assertEqual(ChatGroup.objects.last().name, "Test Group")
        
    def test_create_group_unsuccessfully(self):
        self.client.force_login(self.school_1.support)
        
        url = reverse("messenger:home")
        data = {
            "conversation_type": "chatgroup",   # wrong type
            "name": "Test Group",
            "owner": self.school_1.support,
        }
        response = self.client.post(url, data)
        messages = [*get_messages(response.wsgi_request)]
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(messages[-1]), "Invalid input provided.")
        self.assertEqual(ChatGroup.objects.count(), 0)


class TestConsumers(ChannelsLiveServerTestCase):
    serve_static = True

    # === SetUp ===

    @classmethod
    def _set_chrome_options(cls):
        chrome_options = webdriver.chrome.options.Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_prefs = dict()
        chrome_options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        return chrome_options

    @classmethod
    def _create_driver(cls, stores_logs=False):
        d = DesiredCapabilities.CHROME
        if stores_logs:
            d["goog:loggingPrefs"] = {'browser': 'ALL'}
        return webdriver.Chrome(
            options=cls._set_chrome_options(),
            executable_path="/usr/src/app/chromedriver/chromedriver",
            desired_capabilities=d,
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            cls.driver = cls._create_driver()
        except:
            super().tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()
        super().tearDownClass()

    # === Utility ===

    def _create_user(self,
                     driver,
                     user_type,
                     username="test",
                     password="123456789",
                     first_name="test",
                     last_name="test"):
        user = get_user_model().objects.create_user(
            username=username,
            password=password,
            user_type=user_type,
            first_name=first_name,
            last_name=last_name,
        )
        force_login(user, driver, self.live_server_url)
        return user

    def _create_principal_user(self,
                               username="test",
                               password="123456789",
                               school_name="test school"):
        user = self._create_user(self.driver,
                                 username=username,
                                 password=password,
                                 user_type="SS")
        School.objects.create(name=school_name, support=user)
        return 

    def _create_teacher(self,
                        driver,
                        school=School.objects.last(),
                        username="test",
                        password="123456789",
                        first_name="test",
                        last_name="test"):
        user = self._create_user(driver,
                                 username=username,
                                 password=password,
                                 user_type="T",
                                 first_name=first_name,
                                 last_name=last_name)
        Teacher.objects.create(user=user, school=school)
        return user

    def _create_a_group(self, driver, name="Test Group"):
        """
        Create a chat group in the messenger app.
        return: ChatGroup object
        
        Args:
            name (_str_): name of the group
        """
        self._create_principal_user()
        driver.get(self.live_server_url + reverse("messenger:home"))
        create_group_modal_button = driver.find_element_by_id(
            "create-group-modal-button")
        create_group_modal_button.click()
        create_group_name_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "group-name-field"), ),
            "Group name field did not show up...",
        )
        time.sleep(0.5)
        create_group_name_input.send_keys(name)
        driver.find_element_by_id("create-group-button").click()
        return ChatGroup.objects.last()

    def _add_member_to_group_and_redirect(self, driver, member_user, group_id):
        try:
            chatgroup = ChatGroup.objects.get(group_id=group_id)
            member, _ = Member.objects.get_or_create(user=member_user,
                                                     chatgroup=chatgroup)
            driver.get(self.live_server_url +
                       reverse("messenger:home"))
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, f"group-{group_id}"), ),
                "The group hasn't been added to user's conversations list",
            ).click()
            time.sleep(1)
            return member
        except ChatGroup.DoesNotExist:
            return AssertionError("Chat group does not exist")

    def _post_message(self, driver, message="Test message"):
        send_text_input = driver.find_element_by_id("msg-input")
        send_text_input.send_keys(message)
        send_text_input.send_keys(Keys.ENTER)
        time.sleep(1)

    def _last_message(self, driver):
        message_xpath = f"//div[@id='message-box']/li[last()]/p"
        return WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.XPATH, message_xpath), ),
            "The message wasn't sent back by the socket server...",
        ).get_property("textContent")

    def _is_marked_as_read(self, driver, message_id):
        time.sleep(3)
        mark = driver.find_element_by_id(f"read_{message_id}")
        un_mark = driver.find_element_by_id(f"unread_{message_id}")
        return mark.is_displayed() and not un_mark.is_displayed()

    # === Tests ===

    def test_send_a_message_into_a_group_and_receive_it(self):
        # Create a chat group, navigate to it and send a message
        # by the first browser
        chatgroup = self._create_a_group(self.driver)
        owner_school = chatgroup.owner.school
        chatgroup_url = self.live_server_url + chatgroup.get_absolute_url()
        self.driver.get(chatgroup_url)
        self._post_message(self.driver)
        time.sleep(1)
        self.assertTrue(Message.objects.count() > 0)
        last_message_id = chatgroup.ordered_messages.last().message_id.hex

        # Open another browser, so that you can login with another
        # account and see if the message exists
        driver2 = self._create_driver()
        other_user = self._create_teacher(driver2, 
                                          username="test_teacher", 
                                          school=owner_school)
        self._add_member_to_group_and_redirect(driver2, 
                                               other_user,
                                               chatgroup.group_id)
        last_message = self._last_message(driver2)
        self.assertIn("Test message", last_message)

        # after the other endpoint reads the message, check if the
        # message has been marked as read
        self.assertTrue(last_message_id)
        self.assertTrue(self._is_marked_as_read(self.driver, last_message_id))

        driver2.close()

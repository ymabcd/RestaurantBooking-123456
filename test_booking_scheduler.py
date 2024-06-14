import unittest
from datetime import datetime, timedelta

from booking_scheduler import BookingScheduler
from communication_test import TestableSmsSender, TestableMailSender
from schedule import Customer, Schedule

NOT_ON_THE_HOUR = datetime.strptime("2021/03/26 09:05", "%Y/%m/%d %H:%M")
ON_THE_HOUR = datetime.strptime("2021/03/26 09:00", "%Y/%m/%d %H:%M")
CUSTOMER = Customer("Fake name", "010-1234-5678")
CUSTOMER_WITH_MAIL = Customer("Fake name", "010-1234-5678", "test@test.com")


UNDER_CAPACITY = 1
CAPACITY_PER_HOUR = 3

class SundayBookingScheduler(BookingScheduler):
    def __init__(self, capacity_per_hour):
        super().__init__(capacity_per_hour)

    def get_now(self):
        return datetime.strptime("2021/03/28 17:00", "%Y/%m/%d %H:%M")


class MondayBookingScheduler(BookingScheduler):
    def __init__(self, capacity_per_hour):
        super().__init__(capacity_per_hour)

    def get_now(self):
        return datetime.strptime("2024/06/03 17:00", "%Y/%m/%d %H:%M")


class BookingSchedulerTest(unittest.TestCase):
    def setUp(self):
        self.booking_scheduler = BookingScheduler(CAPACITY_PER_HOUR)
        self.testable_sms_sender = TestableSmsSender()
        self.booking_scheduler.set_sms_sender(self.testable_sms_sender)
        self.testable_mail_sender = TestableMailSender()
        self.booking_scheduler.set_mail_sender(self.testable_mail_sender)

    def test_예약은_정시에만_가능하다_정시가_아닌경우_예약불가(self):
        schedule = Schedule(NOT_ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)
        with self.assertRaises(ValueError):
            self.booking_scheduler.add_schedule(schedule)


    def test_예약은_정시에만_가능하다_정시인_경우_예약가능(self):
        customer = Customer("Fake name", "010-1234-5678")
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)

        self.booking_scheduler.add_schedule(schedule)

        self.assertTrue(self.booking_scheduler.has_schedule(schedule))

    def test_시간대별_인원제한이_있다_같은_시간대에_Capacity_초과할_경우_예외발생(self):
        schedule = Schedule(ON_THE_HOUR, CAPACITY_PER_HOUR, CUSTOMER)
        self.booking_scheduler.add_schedule(schedule)

        with self.assertRaises(ValueError) as context:
            new_schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)
            self.booking_scheduler.add_schedule(new_schedule)

        self.assertEqual("Number of people is over restaurant capacity per hour", str(context.exception))

    def test_시간대별_인원제한이_있다_같은_시간대가_다르면_Capacity_차있어도_스케쥴_추가_성공(self):
        schedule = Schedule(ON_THE_HOUR, CAPACITY_PER_HOUR, CUSTOMER)
        self.booking_scheduler.add_schedule(schedule)

        different_hour = ON_THE_HOUR + timedelta(hours = 1)
        new_schedule = Schedule(different_hour, UNDER_CAPACITY, CUSTOMER)
        self.booking_scheduler.add_schedule(new_schedule)

        self.assertTrue(self.booking_scheduler.has_schedule(new_schedule))

    def test_예약완료시_SMS는_무조건_발송(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)

        self.booking_scheduler.add_schedule(schedule)

        self.assertTrue(self.testable_sms_sender.is_send_method_is_called())

    def test_이메일이_없는_경우에는_이메일_미발송(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER)

        self.booking_scheduler.add_schedule(schedule)

        self.assertEqual(self.testable_mail_sender.get_count_send_mail_is_called(), 0)

    def test_이메일이_있는_경우에는_이메일_발송(self):
        schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER_WITH_MAIL)

        self.booking_scheduler.add_schedule(schedule)

        self.assertEqual(self.testable_mail_sender.get_count_send_mail_is_called(), 1)

    def test_현재날짜가_일요일인_경우_예약불가_예외처리(self):
        self.booking_scheduler = SundayBookingScheduler(CAPACITY_PER_HOUR)

        with self.assertRaises(ValueError):
            new_schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER_WITH_MAIL)
            self.booking_scheduler.add_schedule(new_schedule)
            self.fail()

    def get_now(self):
        return datetime.now()

    def test_현재날짜가_일요일이_아닌경우_예약가능(self):
        self.booking_scheduler = MondayBookingScheduler(CAPACITY_PER_HOUR)

        new_schedule = Schedule(ON_THE_HOUR, UNDER_CAPACITY, CUSTOMER_WITH_MAIL)
        self.booking_scheduler.add_schedule(new_schedule)

        self.assertTrue(self.booking_scheduler.has_schedule(new_schedule))


if __name__ == '__main__':
    unittest.main()

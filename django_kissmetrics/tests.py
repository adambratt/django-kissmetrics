from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.utils.unittest.case import TestCase

from django_kissmetrics import base


class MiscTestCase(TestCase):

    def setUp(self):
        super(MiscTestCase, self).setUp()
        first_name = 'delete'
        last_name = 'me'
        password = 'pass'
        username = '%s%s' % (first_name, last_name)
        self.user = User.objects.create(
            email='%s@test.com' % username,
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

    def tearDown(self):
        self.user.delete()
        super(MiscTestCase, self).tearDown()

    def test_kissmetrics(self):
        self.assertFalse(self.user.kissmetrics_ignore)

        o = base.KISSMetricTask('identify', 'bob@bob.com')
        self.assertEquals("_kmq.push(['identify','bob@bob.com']);", o.toJS())

        o = base.KISSMetricTask('record', 'Viewed Homepage')
        self.assertEquals("_kmq.push(['record','Viewed Homepage']);", o.toJS())

        o = base.KISSMetricTask('record', 'Signed Up', {
            'Plan': 'Pro', 'Amount': 99.95})
        self.assertEquals("_kmq.push(['record','Signed Up',"
                          "{'Amount':'99.95','Plan':'Pro'}]);", o.toJS())

        o = base.KISSMetricTask('set', None, {'gender': 'male'})
        self.assertEquals("_kmq.push(['set',{'gender':'male'}]);", o.toJS())

    def test_get_kissmetrics_instance(self):
        request = RequestFactory()
        request.COOKIES = {}
        km_ai = '1234'
        km_ni = 'asdf'

        # invalid object
        self.assertRaises(ValueError, base.get_kissmetrics_instance, {})

        # no identity error
        self.assertRaises(ValueError, base.get_kissmetrics_instance, request)

        # fetch identity from the cookies
        request.COOKIES = {'km_ai': km_ai, 'km_ni': km_ni}
        km = base.get_kissmetrics_instance(request)
        self.assertEquals(km_ni, km._id)

        # fetch the identity from the user
        request.user = self.user
        km = base.get_kissmetrics_instance(request)
        self.assertEquals(self.user.id, km._id)

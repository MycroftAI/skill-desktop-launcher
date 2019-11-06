from test.integrationtests.skills.skill_tester import SkillTest
import mock


SEARCH_BASE = 'http://www.google.com/search?&sourceid=navclient&btnI=I&q={}'


@mock.patch('mycroft.skills.mycroft_skill.mycroft_skill.DeviceApi.send_email')
def test_runner(skill, example, emitter, loader, m1):
    s = [s for s in loader.skills if s and s.root_dir == skill][0]
    with mock.patch('webbrowser.open') as m:
        ret = SkillTest(skill, example, emitter).run(loader)
        if example.endswith('find.puppies.json'):
            m.assert_called_with(SEARCH_BASE.format('wikipedia%20puppies'))
        elif example.endswith('find.puppies.json'):
            m.assert_called_with(SEARCH_BASE.format('imgur'))
        elif example.endswith('open.tumblr.json'):
            m.assert_called_with(SEARCH_BASE.format('tumblr'))
        elif example.endswith('search.for.kittens.json'):
            m.assert_called_with(SEARCH_BASE.format('youtube%20for%20kittens'))

    if example.endswith('launch.rocket.json'):
        s.register_vocabulary('rocket', 'Application')
        m = mock.Mock()
        s.appmap['rocket'] = [m]
        ret = SkillTest(skill, example, emitter).run(loader)
        m.launch.assert_called_with()
    elif example.endswith('open.notepad.json'):
        s.register_vocabulary('notepad', 'Application')
        m = mock.Mock()
        s.appmap['notepad'] = [m]
        ret = SkillTest(skill, example, emitter).run(loader)
        m.launch.assert_called_with()
    return ret

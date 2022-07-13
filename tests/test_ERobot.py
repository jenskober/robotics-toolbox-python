#!/usr/bin/env python3
"""
Created on Fri May 1 14:04:04 2020
@author: Jesse Haviland
"""

import numpy.testing as nt
import numpy as np
import roboticstoolbox as rtb
from roboticstoolbox import ERobot, ET, ETS, ERobot2, Link
from spatialmath import SE2, SE3
import unittest
import spatialmath as sm
import spatialgeometry as gm
from math import pi, sin, cos


class TestERobot(unittest.TestCase):
    def test_init(self):
        ets = ETS(rtb.ET.Rz())
        robot = ERobot(
            ets, name="myname", manufacturer="I made it", comment="other stuff"
        )
        self.assertEqual(robot.name, "myname")
        self.assertEqual(robot.manufacturer, "I made it")
        self.assertEqual(robot.comment, "other stuff")

    def test_init_ets(self):
        ets = (
            rtb.ET.tx(-0.0825)
            * rtb.ET.Rz()
            * rtb.ET.tx(-0.0825)
            * rtb.ET.tz()
            * rtb.ET.tx(0.1)
        )

        robot = ERobot(ets)
        self.assertEqual(robot.n, 2)
        self.assertIsInstance(robot[0], Link)
        self.assertIsInstance(robot[1], Link)
        self.assertTrue(robot[0].isrevolute)
        self.assertTrue(robot[1].isprismatic)

        self.assertIs(robot[0].parent, None)
        self.assertIs(robot[1].parent, robot[0])
        self.assertIs(robot[2].parent, robot[1])

        self.assertEqual(robot[0].children, [robot[1]])
        self.assertEqual(robot[1].children, [robot[2]])
        self.assertEqual(robot[2].children, [])

    def test_init_elink(self):
        link1 = Link(ETS(ET.Rx()), name="link1")
        link2 = Link(ET.tx(1) * ET.ty(-0.5) * ET.tz(), name="link2", parent=link1)
        link3 = Link(ETS(ET.tx(1)), name="ee_1", parent=link2)
        robot = ERobot([link1, link2, link3])
        self.assertEqual(robot.n, 2)
        self.assertIsInstance(robot[0], Link)
        self.assertIsInstance(robot[1], Link)
        self.assertIsInstance(robot[2], Link)
        self.assertTrue(robot[0].isrevolute)
        self.assertTrue(robot[1].isprismatic)

        self.assertFalse(robot[2].isrevolute)
        self.assertFalse(robot[2].isprismatic)

        self.assertIs(robot[0].parent, None)
        self.assertIs(robot[1].parent, robot[0])
        self.assertIs(robot[2].parent, robot[1])

        self.assertEqual(robot[0].children, [robot[1]])
        self.assertEqual(robot[1].children, [robot[2]])
        self.assertEqual(robot[2].children, [])

        link1 = Link(ETS(ET.Rx()), name="link1")
        link2 = Link(ET.tx(1) * ET.ty(-0.5) * ET.tz(), name="link2", parent="link1")
        link3 = Link(ETS(ET.tx(1)), name="ee_1", parent="link2")
        robot = ERobot([link1, link2, link3])
        self.assertEqual(robot.n, 2)
        self.assertIsInstance(robot[0], Link)
        self.assertIsInstance(robot[1], Link)
        self.assertIsInstance(robot[2], Link)
        self.assertTrue(robot[0].isrevolute)
        self.assertTrue(robot[1].isprismatic)

        self.assertIs(robot[0].parent, None)
        self.assertIs(robot[1].parent, robot[0])
        self.assertIs(robot[2].parent, robot[1])

        self.assertEqual(robot[0].children, [robot[1]])
        self.assertEqual(robot[1].children, [robot[2]])
        self.assertEqual(robot[2].children, [])

    def test_init_elink_autoparent(self):
        links = [
            Link(ETS(ET.Rx()), name="link1"),
            Link(ET.tx(1) * ET.ty(-0.5) * ET.tz(), name="link2"),
            Link(ETS(ET.tx(1)), name="ee_1"),
        ]
        robot = ERobot(links)
        self.assertEqual(robot.n, 2)
        self.assertIsInstance(robot[0], Link)
        self.assertIsInstance(robot[1], Link)
        self.assertIsInstance(robot[2], Link)
        self.assertTrue(robot[0].isrevolute)
        self.assertTrue(robot[1].isprismatic)
        self.assertIs(robot[0].parent, None)
        self.assertIs(robot[1].parent, robot[0])
        self.assertIs(robot[2].parent, robot[1])

        self.assertEqual(robot[0].children, [robot[1]])
        self.assertEqual(robot[1].children, [robot[2]])
        self.assertEqual(robot[2].children, [])

    def test_init_elink_branched(self):
        robot = ERobot(
            [
                Link(ETS(ET.Rz()), name="link1"),
                Link(
                    ETS(ET.tx(1)) * ET.ty(-0.5) * ET.Rz(), name="link2", parent="link1"
                ),
                Link(ETS(ET.tx(1)), name="ee_1", parent="link2"),
                Link(ET.tx(1) * ET.ty(0.5) * ET.Rz(), name="link3", parent="link1"),
                Link(ETS(ET.tx(1)), name="ee_2", parent="link3"),
            ]
        )
        self.assertEqual(robot.n, 3)
        for i in range(5):
            self.assertIsInstance(robot[i], Link)
        self.assertTrue(robot[0].isrevolute)
        self.assertTrue(robot[1].isrevolute)
        self.assertTrue(robot[3].isrevolute)

        self.assertIs(robot[0].parent, None)
        self.assertIs(robot[1].parent, robot[0])
        self.assertIs(robot[2].parent, robot[1])
        self.assertIs(robot[3].parent, robot[0])
        self.assertIs(robot[4].parent, robot[3])

        self.assertEqual(robot[0].children, [robot[1], robot[3]])
        self.assertEqual(robot[1].children, [robot[2]])
        self.assertEqual(robot[2].children, [])
        self.assertEqual(robot[3].children, [robot[4]])
        self.assertEqual(robot[2].children, [])

    def test_init_bases(self):
        e1 = Link()
        e2 = Link()
        e3 = Link(parent=e1)
        e4 = Link(parent=e2)

        with self.assertRaises(ValueError):
            ERobot([e1, e2, e3, e4])

    def test_jindex(self):
        e1 = Link(ETS(ET.Rz()), jindex=0)
        e2 = Link(ETS(ET.Rz()), jindex=1, parent=e1)
        e3 = Link(ETS(ET.Rz()), jindex=2, parent=e2)
        e4 = Link(ETS(ET.Rz()), jindex=0, parent=e3)

        # with self.assertRaises(ValueError):
        ERobot([e1, e2, e3, e4], gripper_links=e4)

    def test_jindex_fail(self):
        e1 = Link(rtb.ETS(rtb.ET.Rz()), jindex=0)
        e2 = Link(rtb.ETS(rtb.ET.Rz()), jindex=1, parent=e1)
        e3 = Link(rtb.ETS(rtb.ET.Rz()), jindex=2, parent=e2)
        e4 = Link(rtb.ETS(rtb.ET.Rz()), jindex=5, parent=e3)

        with self.assertRaises(ValueError):
            ERobot([e1, e2, e3, e4])

        e1 = Link(rtb.ETS(rtb.ET.Rz()), jindex=0)
        e2 = Link(rtb.ETS(rtb.ET.Rz()), jindex=1, parent=e1)
        e3 = Link(rtb.ETS(rtb.ET.Rz()), jindex=2, parent=e2)
        e4 = Link(rtb.ETS(rtb.ET.Rz()), parent=e3)

        with self.assertRaises(ValueError):
            ERobot([e1, e2, e3, e4])

    def test_panda(self):
        panda = rtb.models.ETS.Panda()
        qz = np.array([0, 0, 0, 0, 0, 0, 0])
        qr = panda.qr

        nt.assert_array_almost_equal(panda.qr, qr)
        nt.assert_array_almost_equal(panda.qz, qz)
        nt.assert_array_almost_equal(panda.gravity, np.r_[0, 0, -9.81])

    def test_q(self):
        panda = rtb.models.ETS.Panda()

        q1 = np.array([1.4, 0.2, 1.8, 0.7, 0.1, 3.1, 2.9])
        q2 = [1.4, 0.2, 1.8, 0.7, 0.1, 3.1, 2.9]
        q3 = np.expand_dims(q1, 0)

        panda.q = q1
        nt.assert_array_almost_equal(panda.q, q1)
        panda.q = q2
        nt.assert_array_almost_equal(panda.q, q2)
        panda.q = q3
        nt.assert_array_almost_equal(np.expand_dims(panda.q, 0), q3)

    def test_getters(self):
        panda = rtb.models.ETS.Panda()

        panda.qdd = np.ones((7, 1))
        panda.qd = np.ones((1, 7))
        panda.qdd = panda.qd
        panda.qd = panda.qdd

    def test_control_mode(self):
        panda = rtb.models.ETS.Panda()
        panda.control_mode = "v"
        self.assertEqual(panda.control_mode, "v")

    def test_base(self):
        panda = rtb.models.ETS.Panda()

        pose = sm.SE3()

        panda.base = pose.A
        nt.assert_array_almost_equal(np.eye(4), panda.base.A)

        panda.base = pose
        nt.assert_array_almost_equal(np.eye(4), panda.base.A)

    def test_fkine(self):
        panda = rtb.models.ETS.Panda()
        q1 = np.array([1.4, 0.2, 1.8, 0.7, 0.1, 3.1, 2.9])
        q2 = [1.4, 0.2, 1.8, 0.7, 0.1, 3.1, 2.9]
        q3 = np.expand_dims(q1, 0)

        ans = np.array(
            [
                [-0.50827907, -0.57904589, 0.63746234, 0.44682295],
                [0.83014553, -0.52639462, 0.18375824, 0.16168396],
                [0.22915229, 0.62258699, 0.74824773, 0.96798113],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )

        # panda.q = q1
        nt.assert_array_almost_equal(panda.fkine(q1).A, ans)

    def test_jacob0(self):
        panda = rtb.models.ETS.Panda()
        q1 = np.array([1.4, 0.2, 1.8, 0.7, 0.1, 3.1, 2.9])
        q2 = [1.4, 0.2, 1.8, 0.7, 0.1, 3.1, 2.9]
        q3 = np.expand_dims(q1, 0)
        q4 = np.expand_dims(q1, 1)

        ans = np.array(
            [
                [
                    -1.61683957e-01,
                    1.07925929e-01,
                    -3.41453006e-02,
                    3.35029257e-01,
                    -1.07195463e-02,
                    1.03187865e-01,
                    0.00000000e00,
                ],
                [
                    4.46822947e-01,
                    6.25741987e-01,
                    4.16474664e-01,
                    -8.04745724e-02,
                    7.78257566e-02,
                    -1.17720983e-02,
                    0.00000000e00,
                ],
                [
                    0.00000000e00,
                    -2.35276631e-01,
                    -8.20187641e-02,
                    -5.14076923e-01,
                    -9.98040745e-03,
                    -2.02626953e-01,
                    0.00000000e00,
                ],
                [
                    1.29458954e-16,
                    -9.85449730e-01,
                    3.37672585e-02,
                    -6.16735653e-02,
                    6.68449878e-01,
                    -1.35361558e-01,
                    6.37462344e-01,
                ],
                [
                    9.07021273e-18,
                    1.69967143e-01,
                    1.95778638e-01,
                    9.79165111e-01,
                    1.84470262e-01,
                    9.82748279e-01,
                    1.83758244e-01,
                ],
                [
                    1.00000000e00,
                    -2.26036604e-17,
                    9.80066578e-01,
                    -1.93473657e-01,
                    7.20517510e-01,
                    -1.26028049e-01,
                    7.48247732e-01,
                ],
            ]
        )

        panda.q = q1
        # nt.assert_array_almost_equal(panda.jacob0(), ans)
        nt.assert_array_almost_equal(panda.jacob0(q2), ans)
        nt.assert_array_almost_equal(panda.jacob0(q3), ans)
        nt.assert_array_almost_equal(panda.jacob0(q4), ans)
        self.assertRaises(TypeError, panda.jacob0, "Wfgsrth")

    def test_hessian0(self):
        panda = rtb.models.ETS.Panda()
        q1 = np.array([1.4, 0.2, 1.8, 0.7, 0.1, 3.1, 2.9])
        q2 = [1.4, 0.2, 1.8, 0.7, 0.1, 3.1, 2.9]
        q3 = np.expand_dims(q1, 0)
        q4 = np.expand_dims(q1, 1)

        ans = np.array(
            [
                [
                    [
                        -4.46822947e-01,
                        -6.25741987e-01,
                        -4.16474664e-01,
                        8.04745724e-02,
                        -7.78257566e-02,
                        1.17720983e-02,
                        0.00000000e00,
                    ],
                    [
                        -6.25741987e-01,
                        -3.99892968e-02,
                        -1.39404950e-02,
                        -8.73761859e-02,
                        -1.69634134e-03,
                        -3.44399243e-02,
                        0.00000000e00,
                    ],
                    [
                        -4.16474664e-01,
                        -1.39404950e-02,
                        -4.24230421e-01,
                        -2.17748413e-02,
                        -7.82283735e-02,
                        -2.81325889e-02,
                        0.00000000e00,
                    ],
                    [
                        8.04745724e-02,
                        -8.73761859e-02,
                        -2.17748413e-02,
                        -5.18935898e-01,
                        5.28476698e-03,
                        -2.00682834e-01,
                        0.00000000e00,
                    ],
                    [
                        -7.78257566e-02,
                        -1.69634134e-03,
                        -7.82283735e-02,
                        5.28476698e-03,
                        -5.79159088e-02,
                        -2.88966443e-02,
                        0.00000000e00,
                    ],
                    [
                        1.17720983e-02,
                        -3.44399243e-02,
                        -2.81325889e-02,
                        -2.00682834e-01,
                        -2.88966443e-02,
                        -2.00614904e-01,
                        0.00000000e00,
                    ],
                    [
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                    ],
                ],
                [
                    [
                        -1.61683957e-01,
                        1.07925929e-01,
                        -3.41453006e-02,
                        3.35029257e-01,
                        -1.07195463e-02,
                        1.03187865e-01,
                        0.00000000e00,
                    ],
                    [
                        1.07925929e-01,
                        -2.31853293e-01,
                        -8.08253690e-02,
                        -5.06596965e-01,
                        -9.83518983e-03,
                        -1.99678676e-01,
                        0.00000000e00,
                    ],
                    [
                        -3.41453006e-02,
                        -8.08253690e-02,
                        -3.06951191e-02,
                        3.45709946e-01,
                        -1.01688580e-02,
                        1.07973135e-01,
                        0.00000000e00,
                    ],
                    [
                        3.35029257e-01,
                        -5.06596965e-01,
                        3.45709946e-01,
                        -9.65242924e-02,
                        1.45842251e-03,
                        -3.24608603e-02,
                        0.00000000e00,
                    ],
                    [
                        -1.07195463e-02,
                        -9.83518983e-03,
                        -1.01688580e-02,
                        1.45842251e-03,
                        -1.05221866e-03,
                        2.09794626e-01,
                        0.00000000e00,
                    ],
                    [
                        1.03187865e-01,
                        -1.99678676e-01,
                        1.07973135e-01,
                        -3.24608603e-02,
                        2.09794626e-01,
                        -4.04324654e-02,
                        0.00000000e00,
                    ],
                    [
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                    ],
                ],
                [
                    [
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                    ],
                    [
                        0.00000000e00,
                        -6.34981134e-01,
                        -4.04611266e-01,
                        2.23596800e-02,
                        -7.48714002e-02,
                        -5.93773551e-03,
                        0.00000000e00,
                    ],
                    [
                        0.00000000e00,
                        -4.04611266e-01,
                        2.07481281e-02,
                        -6.83089775e-02,
                        4.72662062e-03,
                        -2.05994912e-02,
                        0.00000000e00,
                    ],
                    [
                        0.00000000e00,
                        2.23596800e-02,
                        -6.83089775e-02,
                        -3.23085806e-01,
                        5.69641385e-03,
                        -1.00311930e-01,
                        0.00000000e00,
                    ],
                    [
                        0.00000000e00,
                        -7.48714002e-02,
                        4.72662062e-03,
                        5.69641385e-03,
                        5.40000550e-02,
                        -2.69041502e-02,
                        0.00000000e00,
                    ],
                    [
                        0.00000000e00,
                        -5.93773551e-03,
                        -2.05994912e-02,
                        -1.00311930e-01,
                        -2.69041502e-02,
                        -9.98142073e-02,
                        0.00000000e00,
                    ],
                    [
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                        0.00000000e00,
                    ],
                ],
                [
                    [
                        -9.07021273e-18,
                        -2.77555756e-17,
                        -2.77555756e-17,
                        -1.11022302e-16,
                        -2.77555756e-17,
                        0.00000000e00,
                        -2.77555756e-17,
                    ],
                    [
                        -1.69967143e-01,
                        -1.97756387e-17,
                        4.11786040e-17,
                        -1.48932398e-16,
                        -5.07612940e-17,
                        -8.38219650e-17,
                        -4.90138154e-17,
                    ],
                    [
                        -1.95778638e-01,
                        1.66579116e-01,
                        -1.38777878e-17,
                        1.04083409e-17,
                        -1.38777878e-17,
                        3.46944695e-18,
                        0.00000000e00,
                    ],
                    [
                        -9.79165111e-01,
                        -3.28841647e-02,
                        -9.97525009e-01,
                        -4.16333634e-17,
                        -1.14491749e-16,
                        1.38777878e-17,
                        -6.24500451e-17,
                    ],
                    [
                        -1.84470262e-01,
                        1.22464303e-01,
                        -3.97312016e-02,
                        7.41195745e-01,
                        -2.77555756e-17,
                        1.12757026e-16,
                        2.77555756e-17,
                    ],
                    [
                        -9.82748279e-01,
                        -2.14206274e-02,
                        -9.87832342e-01,
                        6.67336352e-02,
                        -7.31335770e-01,
                        2.08166817e-17,
                        -6.07153217e-17,
                    ],
                    [
                        -1.83758244e-01,
                        1.27177529e-01,
                        -3.36043908e-02,
                        7.68210453e-01,
                        5.62842325e-03,
                        7.58497864e-01,
                        0.00000000e00,
                    ],
                ],
                [
                    [
                        1.29458954e-16,
                        -1.11022302e-16,
                        8.67361738e-17,
                        -4.16333634e-17,
                        5.55111512e-17,
                        2.77555756e-17,
                        5.55111512e-17,
                    ],
                    [
                        -9.85449730e-01,
                        -6.36381327e-17,
                        -1.02735399e-16,
                        -1.83043043e-17,
                        -5.63484308e-17,
                        8.08886307e-18,
                        1.07112702e-18,
                    ],
                    [
                        3.37672585e-02,
                        9.65806345e-01,
                        8.32667268e-17,
                        -2.55871713e-17,
                        1.07552856e-16,
                        2.08166817e-17,
                        -5.20417043e-18,
                    ],
                    [
                        -6.16735653e-02,
                        -1.90658563e-01,
                        -5.39111251e-02,
                        -6.59194921e-17,
                        -2.77555756e-17,
                        2.38524478e-17,
                        -4.16333634e-17,
                    ],
                    [
                        6.68449878e-01,
                        7.10033786e-01,
                        6.30795483e-01,
                        -8.48905588e-02,
                        0.00000000e00,
                        3.46944695e-17,
                        2.77555756e-17,
                    ],
                    [
                        -1.35361558e-01,
                        -1.24194307e-01,
                        -1.28407717e-01,
                        1.84162966e-02,
                        -1.32869389e-02,
                        2.77555756e-17,
                        -2.08166817e-17,
                    ],
                    [
                        6.37462344e-01,
                        7.37360525e-01,
                        5.99489263e-01,
                        -7.71850655e-02,
                        -4.08633244e-02,
                        2.09458434e-02,
                        0.00000000e00,
                    ],
                ],
                [
                    [
                        0.00000000e00,
                        -6.59521910e-17,
                        -1.31033786e-16,
                        -1.92457571e-16,
                        1.54134782e-17,
                        -7.69804929e-17,
                        1.11140361e-17,
                    ],
                    [
                        0.00000000e00,
                        -2.77555756e-17,
                        7.15573434e-17,
                        1.65666092e-16,
                        1.38777878e-17,
                        -8.67361738e-18,
                        3.46944695e-17,
                    ],
                    [
                        0.00000000e00,
                        -1.98669331e-01,
                        8.67361738e-18,
                        -1.46584134e-16,
                        6.02816408e-17,
                        -3.12250226e-17,
                        6.11490025e-17,
                    ],
                    [
                        0.00000000e00,
                        -9.54435515e-01,
                        4.51380881e-02,
                        1.38777878e-17,
                        1.08420217e-16,
                        3.46944695e-18,
                        6.24500451e-17,
                    ],
                    [
                        0.00000000e00,
                        -2.95400686e-01,
                        -1.24639152e-01,
                        -6.65899738e-01,
                        -4.85722573e-17,
                        -5.20417043e-18,
                        -5.55111512e-17,
                    ],
                    [
                        0.00000000e00,
                        -9.45442009e-01,
                        5.96856167e-02,
                        7.19317248e-02,
                        6.81888149e-01,
                        -2.77555756e-17,
                        1.04083409e-17,
                    ],
                    [
                        0.00000000e00,
                        -2.89432165e-01,
                        -1.18596498e-01,
                        -6.35513913e-01,
                        5.24032975e-03,
                        -6.51338823e-01,
                        0.00000000e00,
                    ],
                ],
            ]
        )

        ans_new = np.empty((7, 6, 7))

        for i in range(7):
            ans_new[i, :, :] = ans[:, :, i]

        nt.assert_array_almost_equal(panda.hessian0(q1), ans_new)
        nt.assert_array_almost_equal(panda.hessian0(q2), ans_new)
        nt.assert_array_almost_equal(panda.hessian0(q3), ans_new)
        nt.assert_array_almost_equal(panda.hessian0(q4), ans_new)
        nt.assert_array_almost_equal(panda.hessian0(J0=panda.jacob0(q1)), ans_new)
        nt.assert_array_almost_equal(panda.hessian0(q1, J0=panda.jacob0(q1)), ans_new)

    def test_manipulability(self):
        panda = rtb.models.ETS.Panda()
        q1 = np.array([1.4, 0.2, 1.8, 0.7, 0.1, 3.1, 2.9])
        q2 = [1.4, 0.2, 1.8, 0.7, 0.1, 3.1, 2.9]

        ans = 0.006559178039088341

        panda.q = q1
        nt.assert_array_almost_equal(panda.manipulability(q2), ans)
        # self.assertRaises(ValueError, panda.manipulability)
        self.assertRaises(TypeError, panda.manipulability, "Wfgsrth")
        self.assertRaises(ValueError, panda.manipulability, [1, 3])

    def test_jacobm(self):
        panda = rtb.models.ETS.Panda()
        q1 = np.array([1.4, 0.2, 1.8, 0.7, 0.1, 3.1, 2.9])
        q2 = [1.4, 0.2, 1.8, 0.7, 0.1, 3.1, 2.9]
        q3 = np.expand_dims(q1, 0)
        q4 = np.expand_dims(q1, 1)

        ans = np.array(
            [
                [1.27080875e-17],
                [2.38242538e-02],
                [6.61029519e-03],
                [8.18202121e-03],
                [7.74546204e-04],
                [-1.10885380e-02],
                [0.00000000e00],
            ]
        )

        panda.q = q1
        nt.assert_array_almost_equal(panda.jacobm(), ans)
        nt.assert_array_almost_equal(panda.jacobm(q2), ans)
        nt.assert_array_almost_equal(panda.jacobm(q3), ans)
        nt.assert_array_almost_equal(panda.jacobm(q4), ans)
        nt.assert_array_almost_equal(panda.jacobm(J=panda.jacob0(q1)), ans)
        # self.assertRaises(ValueError, panda.jacobm)
        self.assertRaises(TypeError, panda.jacobm, "Wfgsrth")
        self.assertRaises(ValueError, panda.jacobm, [1, 3], np.array([1, 5]))
        self.assertRaises(TypeError, panda.jacobm, [1, 3], "qwe")
        self.assertRaises(TypeError, panda.jacobm, [1, 3], panda.jacob0(q1), [1, 2, 3])
        self.assertRaises(
            ValueError, panda.jacobm, [1, 3], panda.jacob0(q1), np.array([1, 2, 3])
        )

    # def test_jacobe(self):
    #     pdh = rtb.models.DH.Panda()
    #     panda = rtb.models.ETS.Panda()
    #     q1 = np.array([1.4, 0.2, 1.8, 0.7, 0.1, 3.1, 2.9])
    #     panda.q = q1

    #     # nt.assert_array_almost_equal(panda.jacobe(), pdh.jacobe(q1))
    #     nt.assert_array_almost_equal(panda.jacobe(q1), pdh.jacobe(q1))

    def test_init2(self):
        l0 = Link()
        l1 = Link(parent=l0)
        r = ERobot([l0, l1], base=sm.SE3.Rx(1.3))
        # r.base_link = l1

        with self.assertRaises(TypeError):
            ERobot(l0, base=sm.SE3.Rx(1.3))

        with self.assertRaises(TypeError):
            ERobot([1, 2], base=sm.SE3.Rx(1.3))

    def test_dict(self):
        panda = rtb.models.Panda()
        panda.grippers[0].links[0].collision.append(gm.Cuboid([1, 1, 1]))
        panda._to_dict()

        wx = rtb.models.wx250s()
        wx._to_dict()

    def test_fkdict(self):
        panda = rtb.models.Panda()
        panda.grippers[0].links[0].collision.append(gm.Cuboid([1, 1, 1]))
        panda._fk_dict()

    def test_elinks(self):
        panda = rtb.models.Panda()
        self.assertEqual(panda.elinks[0], panda.link_dict[panda.elinks[0].name])

    def test_base_link_setter(self):
        panda = rtb.models.Panda()

        with self.assertRaises(TypeError):
            panda.base_link = [1]

    def test_ee_link_setter(self):
        panda = rtb.models.Panda()

        panda.ee_links = panda.links[5]

        with self.assertRaises(TypeError):
            panda.ee_links = [1]  # type: ignore

    def test_qlim(self):
        panda = rtb.models.ETS.Panda()

        self.assertEqual(panda.qlim.shape[0], 2)
        self.assertEqual(panda.qlim.shape[1], panda.n)

    def test_manuf(self):
        panda = rtb.models.ETS.Panda()

        self.assertIsInstance(panda.manufacturer, str)

    def test_complex(self):
        l0 = Link(rtb.ET.tx(0.1) * rtb.ET.Rx())
        l1 = Link(rtb.ET.tx(0.1) * rtb.ET.Ry(), parent=l0)
        l2 = Link(rtb.ET.tx(0.1) * rtb.ET.Rz(), parent=l1)
        l3 = Link(rtb.ET.tx(0.1) * rtb.ET.tx(), parent=l2)
        l4 = Link(rtb.ET.tx(0.1) * rtb.ET.ty(), parent=l3)
        l5 = Link(rtb.ET.tx(0.1) * rtb.ET.tz(), parent=l4)

        r = ERobot([l0, l1, l2, l3, l4, l5])
        q = [1, 2, 3, 1, 2, 3]

        ans = np.array(
            [
                [-0.0, 0.08752679, -0.74761985, 0.41198225, 0.05872664, 0.90929743],
                [
                    1.46443609,
                    2.80993063,
                    0.52675075,
                    -0.68124272,
                    -0.64287284,
                    0.35017549,
                ],
                [
                    -1.04432,
                    -1.80423571,
                    -2.20308833,
                    0.60512725,
                    -0.76371834,
                    -0.2248451,
                ],
                [1.0, 0.0, 0.90929743, 0.0, 0.0, 0.0],
                [0.0, 0.54030231, 0.35017549, 0.0, 0.0, 0.0],
                [0.0, 0.84147098, -0.2248451, 0.0, 0.0, 0.0],
            ]
        )

        nt.assert_array_almost_equal(r.jacob0(q), ans)

    def test_control_mode2(self):
        panda = rtb.models.ETS.Panda()

        panda.control_mode = "p"

        with self.assertRaises(ValueError):
            panda.control_mode = "z"

    def test_dist(self):
        s0 = gm.Cuboid([1, 1, 1], pose=sm.SE3(0, 0, 0))
        s1 = gm.Cuboid([1, 1, 1], pose=sm.SE3(3, 0, 0))
        p = rtb.models.Panda()

        d0, _, _ = p.closest_point(p.q, s0)
        d1, _, _ = p.closest_point(p.q, s1, 5)
        d2, _, _ = p.closest_point(p.q, s1)

        self.assertAlmostEqual(d0, -0.5599999999995913)  # type: ignore
        self.assertAlmostEqual(d1, 2.362147178773918)  # type: ignore
        self.assertAlmostEqual(d2, None)  # type: ignore

    def test_collided(self):
        s0 = gm.Cuboid([1, 1, 1], pose=sm.SE3(0, 0, 0))
        s1 = gm.Cuboid([1, 1, 1], pose=sm.SE3(3, 0, 0))
        p = rtb.models.Panda()

        c0 = p.collided(p.q, s0)
        c1 = p.collided(p.q, s1)

        self.assertTrue(c0)
        self.assertFalse(c1)

    def test_invdyn(self):
        # create a 2 link robot
        # Example from Spong etal. 2nd edition, p. 260
        l1 = Link(ets=ETS(ET.Ry()), m=1, r=[0.5, 0, 0], name="l1")
        l2 = Link(ets=ETS(ET.tx(1)) * ET.Ry(), m=1, r=[0.5, 0, 0], parent=l1, name="l2")
        robot = ERobot([l1, l2], name="simple 2 link")
        z = np.zeros(robot.n)

        # check gravity load
        tau = robot.rne(z, z, z) / 9.81
        nt.assert_array_almost_equal(tau, np.r_[-2, -0.5])

        tau = robot.rne([0, -pi / 2], z, z) / 9.81
        nt.assert_array_almost_equal(tau, np.r_[-1.5, 0])

        tau = robot.rne([-pi / 2, pi / 2], z, z) / 9.81
        nt.assert_array_almost_equal(tau, np.r_[-0.5, -0.5])

        tau = robot.rne([-pi / 2, 0], z, z) / 9.81
        nt.assert_array_almost_equal(tau, np.r_[0, 0])

        # check velocity terms
        robot.gravity = [0, 0, 0]
        q = [0, -pi / 2]
        h = -0.5 * sin(q[1])

        tau = robot.rne(q, [0, 0], z)
        nt.assert_array_almost_equal(tau, np.r_[0, 0] * h)

        tau = robot.rne(q, [1, 0], z)
        nt.assert_array_almost_equal(tau, np.r_[0, -1] * h)

        tau = robot.rne(q, [0, 1], z)
        nt.assert_array_almost_equal(tau, np.r_[1, 0] * h)

        tau = robot.rne(q, [1, 1], z)
        nt.assert_array_almost_equal(tau, np.r_[3, -1] * h)

        # check inertial terms

        d11 = 1.5 + cos(q[1])
        d12 = 0.25 + 0.5 * cos(q[1])
        d21 = d12
        d22 = 0.25

        tau = robot.rne(q, z, [0, 0])
        nt.assert_array_almost_equal(tau, np.r_[0, 0])

        tau = robot.rne(q, z, [1, 0])
        nt.assert_array_almost_equal(tau, np.r_[d11, d21])

        tau = robot.rne(q, z, [0, 1])
        nt.assert_array_almost_equal(tau, np.r_[d12, d22])

        tau = robot.rne(q, z, [1, 1])
        nt.assert_array_almost_equal(tau, np.r_[d11 + d12, d21 + d22])


class TestERobot2(unittest.TestCase):
    def test_plot(self):
        robot = rtb.models.ETS.Planar2()
        e = robot.plot(robot.qz, block=False, name=True)
        e.close()

    def test_teach(self):
        robot = rtb.models.ETS.Planar2()
        e = robot.teach(block=False, name=True)
        e.close()

        e = robot.teach(robot.qz, block=False, name=True)
        e.close()

    def test_plot_with_vellipse(self):
        robot = rtb.models.ETS.Planar2()
        e = robot.plot(
            robot.qz, block=False, name=True, vellipse=True, limits=[1, 2, 1, 2]
        )
        e.step()
        e.close()

    def test_plot_with_fellipse(self):
        robot = rtb.models.ETS.Planar2()
        e = robot.plot(
            robot.qz, block=False, name=True, dellipse=True, limits=[1, 2, 1, 2]
        )
        e.step()
        e.close()


if __name__ == "__main__":  # pragma nocover

    unittest.main()

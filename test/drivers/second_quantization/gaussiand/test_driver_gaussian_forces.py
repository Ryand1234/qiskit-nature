# This code is part of Qiskit.
#
# (C) Copyright IBM 2020, 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

""" Test Gaussian Forces Driver """

import unittest
import warnings
from typing import cast

from test import QiskitNatureTestCase, requires_extra_library

from qiskit_nature.drivers import Molecule, WatsonHamiltonian
from qiskit_nature.drivers.second_quantization import (
    GaussianForcesDriver,
    VibrationalStructureMoleculeDriver,
    VibrationalStructureDriverType,
)
from qiskit_nature.properties.second_quantization.vibrational import VibrationalEnergy


class TestDriverGaussianForces(QiskitNatureTestCase):
    """Gaussian Forces Driver tests."""

    _JFC_MOLECULE_EXPECTED = [
        [352.3005875, 2, 2],
        [-352.3005875, -2, -2],
        [631.6153975, 1, 1],
        [-631.6153975, -1, -1],
        [115.653915, 4, 4],
        [-115.653915, -4, -4],
        [115.653915, 3, 3],
        [-115.653915, -3, -3],
        [-15.341901966295344, 2, 2, 2],
        [-88.2017421687633, 1, 1, 2],
        [38.72849649956234, 4, 4, 2],
        [38.72849649956234, 3, 3, 2],
        [0.4207357291666667, 2, 2, 2, 2],
        [4.9425425, 1, 1, 2, 2],
        [1.6122932291666665, 1, 1, 1, 1],
        [-4.194299375, 4, 4, 2, 2],
        [-4.194299375, 3, 3, 2, 2],
        [-10.205891875, 4, 4, 1, 1],
        [-10.205891875, 3, 3, 1, 1],
        [1.8255064583333331, 4, 4, 4, 4],
        [3.507156666666667, 4, 4, 4, 3],
        [10.160466875, 4, 4, 3, 3],
        [-3.507156666666667, 4, 3, 3, 3],
        [1.8255065625, 3, 3, 3, 3],
    ]

    _LOG_FILE_EXPECTED = [
        [352.3005875, 2, 2],
        [-352.3005875, -2, -2],
        [631.6153975, 1, 1],
        [-631.6153975, -1, -1],
        [115.653915, 4, 4],
        [-115.653915, -4, -4],
        [115.653915, 3, 3],
        [-115.653915, -3, -3],
        [-15.341901966295344, 2, 2, 2],
        [-88.2017421687633, 1, 1, 2],
        [42.40478531359112, 4, 4, 2],
        [26.25167512727164, 4, 3, 2],
        [2.2874639206341865, 3, 3, 2],
        [0.4207357291666667, 2, 2, 2, 2],
        [4.9425425, 1, 1, 2, 2],
        [1.6122932291666665, 1, 1, 1, 1],
        [-4.194299375, 4, 4, 2, 2],
        [-4.194299375, 3, 3, 2, 2],
        [-10.20589125, 4, 4, 1, 1],
        [-10.20589125, 3, 3, 1, 1],
        [2.2973803125, 4, 4, 4, 4],
        [2.7821204166666664, 4, 4, 4, 3],
        [7.329224375, 4, 4, 3, 3],
        [-2.7821200000000004, 4, 3, 3, 3],
        [2.2973803125, 3, 3, 3, 3],
    ]

    @requires_extra_library
    def test_driver_jcf(self):
        """Test the driver works with job control file"""
        driver = GaussianForcesDriver(
            [
                "#p B3LYP/6-31g Freq=(Anharm) Int=Ultrafine SCF=VeryTight",
                "",
                "CO2 geometry optimization B3LYP/6-31g",
                "",
                "0 1",
                "C  -0.848629  2.067624  0.160992",
                "O   0.098816  2.655801 -0.159738",
                "O  -1.796073  1.479446  0.481721",
                "",
                "",
            ]
        )
        result = driver.run()
        self._check_driver_result(TestDriverGaussianForces._JFC_MOLECULE_EXPECTED, result)

    @requires_extra_library
    def test_driver_molecule(self):
        """Test the driver works with Molecule"""
        molecule = Molecule(
            geometry=[
                ("C", [-0.848629, 2.067624, 0.160992]),
                ("O", [0.098816, 2.655801, -0.159738]),
                ("O", [-1.796073, 1.479446, 0.481721]),
            ],
            multiplicity=1,
            charge=0,
        )
        driver = VibrationalStructureMoleculeDriver(
            molecule, basis="6-31g", driver_type=VibrationalStructureDriverType.GAUSSIAN_FORCES
        )
        result = driver.run()
        self._check_driver_result(TestDriverGaussianForces._JFC_MOLECULE_EXPECTED, result)

    def test_driver_logfile(self):
        """Test the driver works with logfile (Gaussian does not need to be installed)"""

        driver = GaussianForcesDriver(
            logfile=self.get_resource_path(
                "test_driver_gaussian_log.txt", "drivers/second_quantization/gaussiand"
            )
        )

        result = driver.run()
        self._check_driver_result(TestDriverGaussianForces._LOG_FILE_EXPECTED, result)

    def _check_driver_result(self, expected_watson_data, prop):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            expected_watson = WatsonHamiltonian(expected_watson_data, 4)
        expected = VibrationalEnergy.from_legacy_driver_result(expected_watson)
        true_vib_energy = cast(VibrationalEnergy, prop.get_property(VibrationalEnergy))

        with self.subTest("one-body terms"):
            expected_one_body = expected.get_vibrational_integral(1)
            true_one_body = true_vib_energy.get_vibrational_integral(1)
            self._check_integrals_are_close(expected_one_body, true_one_body)

        with self.subTest("two-body terms"):
            expected_two_body = expected.get_vibrational_integral(2)
            true_two_body = true_vib_energy.get_vibrational_integral(2)
            self._check_integrals_are_close(expected_two_body, true_two_body)

        with self.subTest("three-body terms"):
            expected_three_body = expected.get_vibrational_integral(3)
            true_three_body = true_vib_energy.get_vibrational_integral(3)
            self._check_integrals_are_close(expected_three_body, true_three_body)

    def _check_integrals_are_close(self, expected, truth):
        for exp, true in zip(expected.integrals, truth.integrals):
            self.assertAlmostEqual(true[0], exp[0])
            self.assertEqual(true[1], exp[1])


if __name__ == "__main__":
    unittest.main()

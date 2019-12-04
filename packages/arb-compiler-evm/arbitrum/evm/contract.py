# Copyright 2019, Offchain Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import eth_utils
from importlib_resources import read_text
import json

from .compile import generate_evm_code
from .. import compile_program


class Contract:
    def __init__(self, contractInfo):
        self.address_string = contractInfo["address"]
        self.address = eth_utils.to_int(hexstr=self.address_string)
        self.code = bytes.fromhex(contractInfo["code"][2:])
        self.storage = {}
        if "storage" in contractInfo:
            raw_storage = contractInfo["storage"]
            for item in raw_storage:
                key = eth_utils.to_int(hexstr=item)
                self.storage[key] = eth_utils.to_int(hexstr=raw_storage[item])

    def __repr__(self):
        return "ArbContract({})".format(self.address_string)


def create_evm_vm(contracts, should_optimize=True):
    raw_contract_templates_data = read_text("arbitrum.evm", "contract-templates.json")
    raw_contract_templates = json.loads(raw_contract_templates_data)
    token_templates = {}
    for raw_contract in raw_contract_templates:
        token_templates[raw_contract["name"]] = raw_contract

    token_templates["ArbERC20"][
        "address"
    ] = "0xfffffffffffffffffffffffffffffffffffffffe"
    token_templates["ArbERC721"][
        "address"
    ] = "0xfffffffffffffffffffffffffffffffffffffffd"
    contracts.append(Contract(token_templates["ArbERC20"]))
    contracts.append(Contract(token_templates["ArbERC721"]))
    code = {}
    storage = {}
    for contract in contracts:
        code[contract.address] = contract.code
        storage[contract.address] = contract.storage

    initial_block, code = generate_evm_code(code, storage)

    return compile_program(initial_block, code, should_optimize)

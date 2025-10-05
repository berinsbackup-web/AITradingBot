import asyncio
from core.reward_scheme import RewardScheme

class TradingEnv:
    def __init__(self, data_provider, portfolio_mgr):
        self.data_provider = data_provider
        self.portfolio_mgr = portfolio_mgr
        self.current_step = 0
        self.reward_scheme = RewardScheme(self.portfolio_mgr)
        
    async def reset(self):
        await self.data_provider.reset()
        self.portfolio_mgr.reset()
        self.reward_scheme.reset()
        self.current_step = 0
        obs = await self.data_provider.next()
        return self._get_observation(obs)

    async def step(self, action):
        # Execute action in portfolio manager, returning executed trade qty
        trade_executed = self.portfolio_mgr.execute(action)
        obs = await self.data_provider.next()
        reward = self.reward_scheme.compute(obs, action, trade_executed)
        done = self._check_done()
        info = {"portfolio": self.portfolio_mgr.snapshot()}
        self.current_step += 1
        return self._get_observation(obs), reward, done, info

    def _get_observation(self, obs):
        # Extend obs with any processed/normalized data
        return obs

    def _check_done(self):
        # Define stopping conditions—for example, end of data or max steps
        return False
